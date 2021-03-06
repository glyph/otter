"""
Test to negative scenarios for a scaling policy.
"""
from test_repo.autoscale.fixtures import AutoscaleFixture
from autoscale.status_codes import HttpStatusCodes
import sys


class ScalingPolicyNegative(AutoscaleFixture):

    """
    Verify negative scenarios for a scaling policy.
    """

    def setUp(self):
        """
        Create a scaling group.
        """
        super(ScalingPolicyNegative, self).setUp()
        self.negative_num = -0.1
        create_resp = self.autoscale_behaviors.create_scaling_group_min()
        self.group = create_resp.entity
        self.resources.add(self.group.id,
                           self.autoscale_client.delete_scaling_group)

    def test_scaling_policy_nonexistant(self):
        """
        Negative test: A newly created scaling group does not contain a
        scaling policy, by default.
        """
        list_policy_resp = self.autoscale_client.list_policies(self.group.id)
        list_policy = (list_policy_resp.entity).policies
        self.assertEquals(
            list_policy_resp.status_code, 200,
            msg='List scaling policies for group {0} failed with {0}'
            .format(self.group.id, list_policy_resp.status_code))
        self.validate_headers(list_policy_resp.headers)
        self.assertEquals(
            list_policy, [],
            msg='Some scaling policies exist on the scaling group {0}'
            .format(self.group.id))

    def test_scaling_policy_name_blank(self):
        """
        Negative Test: Scaling policy should not get created with an empty name.
        """
        expected_status_code = HttpStatusCodes.BAD_REQUEST
        error_create_resp = self.autoscale_client.create_policy(
            group_id=self.group.id,
            name='',
            cooldown=self.sp_cooldown,
            change=self.sp_change,
            policy_type=self.sp_policy_type)
        create_error = error_create_resp.entity
        self.assertEquals(
            error_create_resp.status_code, expected_status_code,
            msg='Create scaling policy succeeded with invalid request: {0} '
            'for group {1}'.format(error_create_resp.status_code,
                                   self.group.id))
        self.assertTrue(
            create_error is None,
            msg='Create scaling policy with invalid request returned: {0}'
            ' for group {1}'.format(create_error, self.group.id))

    def test_scaling_policy_name_whitespace(self):
        """
        Negative test: Scaling policy should not get created with name as
        whitespace.
        """
        expected_status_code = HttpStatusCodes.BAD_REQUEST
        error_create_resp = self.autoscale_client.create_policy(
            group_id=self.group.id,
            name='  ',
            cooldown=self.sp_cooldown,
            change=self.sp_change,
            policy_type=self.sp_policy_type)
        create_error = error_create_resp.entity
        self.assertEquals(
            error_create_resp.status_code, expected_status_code,
            msg='Create scaling policy succeeded with invalid request: {0}'
            ' for group {1}'.format(error_create_resp.status_code,
                                    self.group.id))
        self.assertTrue(
            create_error is None,
            msg='Create scaling policy with invalid request returned: {0}'
            ' for group {1}'.format(create_error, self.group.id))

    def test_scaling_policy_cooldown_lessthan_zero(self):
        """
        Negative Test: Scaling policy should not get created with
        cooldown less than zero.
        """
        expected_status_code = HttpStatusCodes.BAD_REQUEST
        error_create_resp = self.autoscale_client.create_policy(
            group_id=self.group.id,
            name=self.sp_name,
            cooldown='-00.01',
            change=self.sp_change,
            policy_type=self.sp_policy_type)
        create_error = error_create_resp.entity
        self.assertEquals(
            error_create_resp.status_code, expected_status_code,
            msg='Create scaling policy succeeded with invalid request: {0}'
            ' for group {1}'.format(error_create_resp.status_code,
                                    self.group.id))
        self.assertTrue(
            create_error is None,
            msg='Create scaling policy with invalid request returned: {0}'
            ' for group {1}'.format(create_error, self.group.id))

    def test_scaling_policy_change_lessthan_zero(self):
        """
        Negative Test: Scaling policy should not get created with change
        less than zero.
        """
        expected_status_code = HttpStatusCodes.BAD_REQUEST
        error_create_resp = self.autoscale_client.create_policy(
            group_id=self.group.id,
            name=self.sp_name,
            cooldown=self.sp_cooldown,
            change='0.001')
        create_error = error_create_resp.entity
        self.assertEquals(
            error_create_resp.status_code, expected_status_code,
            msg='Create scaling policy succeeded with invalid request: {0}'
            ' for group {1}'.format(error_create_resp.status_code,
                                    self.group.id))
        self.assertTrue(
            create_error is None,
            msg='Create scaling policy with invalid request returned: {0}'
            ' for group {1}'.format(create_error, self.group.id))

    def test_get_invalid_policy_id(self):
        """
        Negative Test: Get policy with invalid policy id should fail with
        resource not found 404
        """
        policy = 13344
        expected_status_code = HttpStatusCodes.NOT_FOUND
        error_create_resp = self.autoscale_client.get_policy_details(
            group_id=self.group.id,
            policy_id=policy)
        create_error = error_create_resp.entity
        self.assertEquals(
            error_create_resp.status_code, expected_status_code,
            msg='Create policies succeeded with invalid request: {0}'
            ' for group {1}'.format(error_create_resp.status_code,
                                    self.group.id))
        self.assertTrue(
            create_error is None,
            msg='Create policies with invalid request returned: {0}'
            ' for group {1}'.format(create_error, self.group.id))

    def test_update_invalid_policy_id(self):
        """
        Negative Test: Update policy with invalid policy id should fail with
        resource not found 404
        """
        policy = 13344
        expected_status_code = HttpStatusCodes.NOT_FOUND
        error_create_resp = self.autoscale_client.update_policy(
            group_id=self.group.id,
            policy_id=policy,
            name=self.sp_name,
            cooldown=self.sp_cooldown,
            change=self.sp_change,
            policy_type=self.sp_policy_type)
        create_error = error_create_resp.entity
        self.assertEquals(
            error_create_resp.status_code, expected_status_code,
            msg='Create policies succeeded with invalid request: {0}'
            ' for group {1}'.format(error_create_resp.status_code,
                                    self.group.id))
        self.assertTrue(
            create_error is None,
            msg='Create policies with invalid request returned: {0}'
            ' for group {1}'.format(create_error, self.group.id))

    def test_get_policy_after_deletion(self):
        """
        Negative Test: Get policy when policy is deleted should fail with
        resource not found 404
        """
        policy = self.autoscale_behaviors.create_policy_min(self.group.id)
        del_resp = self.autoscale_client.delete_scaling_policy(
            group_id=self.group.id,
            policy_id=policy['id'])
        self.assertEquals(
            del_resp.status_code, 204,
            msg='Delete policy failed for group {0}'.format(self.group.id))
        expected_status_code = HttpStatusCodes.NOT_FOUND
        error_create_resp = self.autoscale_client.get_policy_details(
            group_id=self.group.id,
            policy_id=policy['id'])
        create_error = error_create_resp.entity
        self.assertEquals(
            error_create_resp.status_code, expected_status_code,
            msg='Get policies succeeded for deleted policy request: {0}'
            ' for group {1}'.format(error_create_resp.status_code,
                                    self.group.id))
        self.assertTrue(
            create_error is None,
            msg='Create policies with invalid request returned: {0}'
            ' for group {1}'.format(create_error, self.group.id))

    def test_update_policy_after_deletion(self):
        """
        Negative Test: Update policy when policy is deleted should fail with
        resource not found 404
        """
        policy = self.autoscale_behaviors.create_policy_min(self.group.id)
        del_resp = self.autoscale_client.delete_scaling_policy(
            group_id=self.group.id,
            policy_id=policy['id'])
        self.assertEquals(
            del_resp.status_code, 204, msg='Delete policy failed for group '
            '{0}'.format(self.group.id))
        expected_status_code = HttpStatusCodes.NOT_FOUND
        error_create_resp = self.autoscale_client.update_policy(
            group_id=self.group.id,
            policy_id=policy[
                'id'],
            name=self.sp_name,
            cooldown=self.sp_cooldown,
            change=self.sp_change,
            policy_type=self.sp_policy_type)
        create_error = error_create_resp.entity
        self.assertEquals(
            error_create_resp.status_code, expected_status_code,
            msg='Update policy after deletion succeeded with : {0}, '
            'policy/groupid: {1} / {2}'
            .format(error_create_resp.status_code,
                    self.group.id, policy['id']))
        self.assertTrue(
            create_error is None,
            msg='Create policies with invalid request returned: {0}'
            ' for group {1}'.format(create_error, self.group.id))

    def test_scaling_policy_maxint_change(self):
        """
        Negative test: Test scaling policy when change is maxint does not
        fail with 400.
        """
        change = sys.maxint
        create_resp = self.autoscale_client.create_policy(
            group_id=self.group.id,
            name=self.sp_name,
            cooldown=self.gc_cooldown,
            change=change,
            policy_type=self.sp_policy_type)
        policy = create_resp.entity
        self.assertEquals(
            create_resp.status_code, 201,
            msg='Create scaling policy failed with maxint as change: {0}'
            'for group {1}'.format(create_resp.status_code, self.group.id))
        self.assertTrue(
            policy is not None,
            msg='Create scaling policy failed: {0} for group {1}'
            .format(policy, self.group.id))

    def test_scaling_policy_max_cooldown(self):
        """
        Negative test: Create scaling policy with cooldown over max fails
        with response code 400.
        """
        create_resp = self.autoscale_client.create_policy(
            group_id=self.group.id,
            name=self.sp_name,
            cooldown=self.max_cooldown + 1,
            change=self.sp_change,
            policy_type=self.sp_policy_type)
        self.assertEquals(
            create_resp.status_code, 400,
            msg='Created scaling policy with cooldown over 24 hrs '
            'with response code: {0} for group {1}'
            .format(create_resp.status_code, self.group.id))

    def test_scaling_policy_invalid_type(self):
        """
        Negative test: Create scaling policy with invalid type will result
        in response code 400.
        """
        create_resp = self.autoscale_client.create_policy(
            group_id=self.group.id,
            name=self.sp_name,
            cooldown=self.sp_cooldown,
            change=self.sp_change,
            policy_type='myowntype')
        self.assertEquals(
            create_resp.status_code, 400,
            msg='Created scaling policy with invalid type with response code: '
            '{0} for group {1}'.format(create_resp.status_code, self.group.id))
