"""
System tests for execute updated policies
"""
from time import sleep

from cafe.drivers.unittest.decorators import tags

from test_repo.autoscale.fixtures import AutoscaleFixture


class ExecuteUpdatedPoliciesTest(AutoscaleFixture):

    """
    System tests to verify execute updated scaling policies scenarios,
    such that each policy executes after policy cooldown is met
    """

    def setUp(self):
        """
        Create a scaling group with min entities>0, scale up with cooldown=1
        second and execute the policy
        """
        super(ExecuteUpdatedPoliciesTest, self).setUp()
        self.cooldown = 1
        self.create_group_response = \
            self.autoscale_behaviors.create_scaling_group_given(
                gc_min_entities=self.gc_min_entities_alt,
                gc_cooldown=0)
        self.group = self.create_group_response.entity
        self.policy_up = {'change': 2, 'cooldown': self.cooldown}
        self.policy = self.autoscale_behaviors.create_policy_webhook(
            group_id=self.group.id,
            policy_data=self.policy_up,
            execute_policy=True)
        self.resources.add(self.group, self.empty_scaling_group)

    @tags(speed='slow', convergence='yes')
    def test_update_policy_from_change_to_desired_capacity_scale_down(self):
        """
        Update the existing scale up policy from change to desired capacity,
        dc set to minentities so that the policy when executed scales down
        """
        upd_desired_capacity = self.group.groupConfiguration.minEntities
        sleep(self.cooldown)
        upd_policy_to_desired_capacity_execute = \
            self._update_execute_policy_dc(
                self.group.id,
                self.policy['policy_id'], upd_desired_capacity)
        self.assertEquals(
            upd_policy_to_desired_capacity_execute, 202,
            msg='Executing the updated policy with desired capacity failed '
            'with {0} for group {1}'
            .format(upd_policy_to_desired_capacity_execute, self.group.id))
        self.wait_for_expected_number_of_active_servers(
            group_id=self.group.id,
            expected_servers=self.group.groupConfiguration.minEntities)
        self.assert_servers_deleted_successfully(
            self.group.launchConfiguration.server.name,
            self.group.groupConfiguration.minEntities)

    @tags(speed='quick', convergence='yes')
    def test_update_policy_from_change_to_desired_capacity_scale_up(self):
        """
        Update the existing scale up policy from change to desired capacity,
        such that the policy when executed scales up
        """
        upd_desired_capacity = self.group.groupConfiguration.minEntities + \
            self.policy_up['change'] + 1
        sleep(self.cooldown)
        upd_policy_to_desired_capacity_execute = \
            self._update_execute_policy_dc(
                self.group.id,
                self.policy['policy_id'], upd_desired_capacity)
        self.assertEquals(
            upd_policy_to_desired_capacity_execute, 202,
            msg='Executing the updated policy with desired capacity failed '
            'with {0} for group {1}'
            .format(upd_policy_to_desired_capacity_execute, self.group.id))
        self.check_for_expected_number_of_building_servers(
            group_id=self.group.id,
            expected_servers=upd_desired_capacity)

    @tags(speed='slow', convergence='yes')
    def test_update_policy_desired_capacity_below_minentities(self):
        """
        Update a scale up via 'change', to a scale down policy via
        'desiredCapacity', with desiredCapacity set to be less than minentities
        and execute the policy.  (results in active servers=minentities)
        """
        upd_desired_capacity = self.group.groupConfiguration.minEntities - 1
        sleep(self.cooldown)
        upd_policy_to_desired_capacity_execute = \
            self._update_execute_policy_dc(
                self.group.id,
                self.policy['policy_id'], upd_desired_capacity)
        self.assertEquals(
            upd_policy_to_desired_capacity_execute, 202,
            msg='Executing the updated policy with desired capacity failed '
            'with {0} for group {1}'
            .format(upd_policy_to_desired_capacity_execute, self.group.id))
        self.wait_for_expected_number_of_active_servers(
            group_id=self.group.id,
            expected_servers=self.group.groupConfiguration.minEntities)

    @tags(speed='quick', convergence='yes')
    def test_update_policy_desired_capacity_over_25(self):
        """
        Update the desired capacity to scale up by setting desired capacity >
        25 and execute. (Results in active servers = 26 in the scaling group)
        """
        sleep(self.cooldown)
        upd_desired_capacity = 26
        sleep(self.cooldown)
        upd_policy_to_desired_capacity_execute = \
            self._update_execute_policy_dc(
                self.group.id,
                self.policy['policy_id'], upd_desired_capacity)
        self.assertEquals(
            upd_policy_to_desired_capacity_execute, 202,
            msg='Executing the updated policy with desired capacity failed '
            'with {0} for group {1}'
            .format(upd_policy_to_desired_capacity_execute, self.group.id))
        # We don't want to time-scale this one because of throttling if this
        # is a convergence tenant - there are 26 servers, and convergence can
        # only build 3 per cycle.  This might take longer than
        # the worker would.
        self.check_for_expected_number_of_building_servers(
            group_id=self.group.id,
            expected_servers=26, time_scale=False)

    @tags(speed='slow', convergence='yes')
    def test_update_scale_up_to_scale_down(self):
        """
        Update a scale up policy to scale down by the same change and execute
        such a policy to result in active servers = minentities on the scaling
        group
        """
        change = - self.policy_up['change']
        sleep(self.cooldown)
        upd_to_scale_down_execute = self._update_execute_policy(
            self.group.id,
            self.policy['policy_id'], change)
        self.assertEquals(
            upd_to_scale_down_execute, 202,
            msg='Executing the updated scale down policy failed with {0} '
            'for group {1}'.format(upd_to_scale_down_execute, self.group.id))
        self.wait_for_expected_number_of_active_servers(
            group_id=self.group.id,
            expected_servers=self.group.groupConfiguration.minEntities)
        self.assert_servers_deleted_successfully(
            self.group.launchConfiguration.server.name,
            self.group.groupConfiguration.minEntities)

    @tags(speed='slow', convergence='yes')
    def test_update_minentities_and_scale_down(self):
        """
        Create a scaling group with min entities > 0, scale up (setup) update
        new_minentities to be 1, verify active servers = minentities+scale up.
        Execute scale down with change = new_minenetities and verify scale down
        """
        new_minentities = 1
        self.autoscale_client.update_group_config(
            group_id=self.group.id,
            name=self.group.groupConfiguration.name,
            cooldown=self.group.groupConfiguration.cooldown,
            min_entities=new_minentities,
            max_entities=self.group.groupConfiguration.maxEntities,
            metadata={})
        self.wait_for_expected_number_of_active_servers(
            group_id=self.group.id,
            expected_servers=(self.group.groupConfiguration.minEntities +
                              self.policy_up['change']))
        change = - (self.policy_up[
                    'change'] + self.group.groupConfiguration.minEntities) + 1
        sleep(self.cooldown)
        upd_to_scale_down_execute = self._update_execute_policy(
            self.group.id,
            self.policy['policy_id'], change)
        self.assertEquals(
            upd_to_scale_down_execute, 202,
            msg='Executing the updated scale down policy failed with {0} '
            'for group {1}'.format(upd_to_scale_down_execute, self.group.id))
        self.wait_for_expected_number_of_active_servers(
            group_id=self.group.id,
            expected_servers=new_minentities)
        self.assert_servers_deleted_successfully(
            self.group.launchConfiguration.server.name,
            new_minentities)

    def _update_execute_policy_dc(self, group_id, policy_id, policy_data):
        """
        Updates any given policy to desired capacity and executes the policy.
        Returns the response code of the updated policy's execution
        """
        get_policy = self.autoscale_client.get_policy_details(
            group_id, policy_id)
        policy_b4_update = get_policy.entity
        self.autoscale_client.update_policy(
            group_id=group_id,
            policy_id=policy_id,
            name=policy_b4_update.name,
            cooldown=policy_b4_update.cooldown,
            desired_capacity=policy_data,
            policy_type=policy_b4_update.type)
        execute_upd_policy = self.autoscale_client.execute_policy(
            group_id, policy_id)
        return execute_upd_policy.status_code

    def _update_execute_policy(self, group_id, policy_id, policy_data):
        """
        Updates any given policy to change and executes the policy.
        Returns the response code of the updated policy's execution
        """
        get_policy = self.autoscale_client.get_policy_details(
            group_id, policy_id)
        policy_b4_update = get_policy.entity
        self.autoscale_client.update_policy(
            group_id=group_id,
            policy_id=policy_id,
            name=policy_b4_update.name,
            cooldown=policy_b4_update.cooldown,
            change=policy_data,
            policy_type=policy_b4_update.type)
        execute_upd_policy = self.autoscale_client.execute_policy(
            group_id, policy_id)
        return execute_upd_policy.status_code
