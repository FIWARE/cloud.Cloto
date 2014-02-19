__author__ = 'artanis'

# -*- coding: utf-8 -*-
from lettuce import step, world, before
from nose.tools import assert_equals, assert_in
from commons.rest_utils import RestUtils
from commons.constants import RULE_ID, SERVER_ID
from commons.configuration import HEADERS, TENANT_ID
from commons.errors import ERROR_CODE_ERROR, INVALID_JSON, INCORRECT_SERVER_ID
import commons.utils as Utils

api_utils = RestUtils()


@before.each_scenario
def setup(scenario):

    #Set default headers with correct token before every scenario
    world.headers = HEADERS


@step(u'a created "([^"]*)" inside tenant')
def set_tenant_and_server_id(step, server_id):

    world.tenant_id = TENANT_ID
    world.server_id = server_id


@step(u'I create a rule with "([^"]*)", "([^"]*)" and "([^"]*)"')
def when_i_create_a_rule_with_group1_group2_and_group3(step, rule_name, rule_condition, rule_action):

    world.rule_name, world.rule_condition, world.rule_action = Utils.create_rule_parameters(rule_name, rule_condition,
                                                                                            rule_action)

    world.req = api_utils.create_rule(tenant_id=world.tenant_id, server_id=world.server_id, rule_name=world.rule_name,
                                      condition=world.rule_condition, action=world.rule_action)


@step(u'Then the rule is saved in Policy Manager')
def then_the_rule_is_saved_in_policy_manager(step):

    assert world.req.ok, 'Invalid HTTP status code. Status Code obtained is: {}'.format(world.req.status_code)
    response = world.req.json()
    assert_equals(response[SERVER_ID], world.server_id, INCORRECT_SERVER_ID.format(world.server_id,
                                                                                   response[SERVER_ID]))
    assert_in(RULE_ID, response.keys(), INVALID_JSON.format(response))
