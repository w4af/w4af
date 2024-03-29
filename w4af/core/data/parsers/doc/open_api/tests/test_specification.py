# -*- coding: UTF-8 -*-
"""
test_specification.py

Copyright 2018 Andres Riancho

This file is part of w4af, https://w4af.net/ .

w4af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w4af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w4af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""
import unittest
import datetime

from w4af.core.data.parsers.doc.open_api.parameters import ParameterHandler
from w4af.core.data.parsers.doc.url import URL
from w4af.core.data.dc.headers import Headers
from w4af.core.data.url.HTTPResponse import HTTPResponse
from w4af.core.data.parsers.doc.open_api.specification import SpecificationHandler
from w4af.core.data.parsers.doc.open_api.tests.example_specifications import (NoParams,
                                                                              IntParamQueryString,
                                                                              IntParamPath,
                                                                              StringParamQueryString,
                                                                              StringParamJson,
                                                                              StringParamHeader,
                                                                              IntParamJson,
                                                                              ArrayStringItemsQueryString,
                                                                              ArrayIntItemsQueryString,
                                                                              IntParamNoModelJson,
                                                                              ComplexDereferencedNestedModel,
                                                                              DereferencedPetStore,
                                                                              NestedModel,
                                                                              NestedLoopModel,
                                                                              ArrayModelItems,
                                                                              MultiplePathsAndHeaders)


class TestSpecification(unittest.TestCase):

    @staticmethod
    def generate_response(specification_as_string):
        url = URL('http://www.w4af.com/swagger.json')
        headers = Headers([('content-type', 'application/json')])
        return HTTPResponse(200, specification_as_string, headers,
                            url, url, _id=1)

    def test_no_params(self):
        specification_as_string = NoParams().get_specification()
        http_response = self.generate_response(specification_as_string)
        handler = SpecificationHandler(http_response)

        data = [d for d in handler.get_api_information()]

        self.assertEqual(len(data), 1)

        (spec, api_resource_name, resource,
         operation_name, operation, parameters) = data[0]

        self.assertEqual(api_resource_name, 'random')
        self.assertEqual(operation_name, 'get_random')
        self.assertEqual(operation.consumes, [])
        self.assertEqual(operation.produces, [])
        self.assertEqual(operation.params, {})
        self.assertEqual(operation.path_name, '/random')

    def test_simple_int_param_in_qs(self):
        specification_as_string = IntParamQueryString().get_specification()
        http_response = self.generate_response(specification_as_string)
        handler = SpecificationHandler(http_response)

        data = [d for d in handler.get_api_information()]

        # The specification says that this query string parameter is not
        # required, thus we get two operations, one for the parameter with
        # a value and another without the parameter
        self.assertEqual(len(data), 2)

        (spec, api_resource_name, resource,
         operation_name, operation, parameters) = data[0]

        self.assertEqual(api_resource_name, 'pets')
        self.assertEqual(operation_name, 'findPets')
        self.assertEqual(operation.consumes, ['application/json'])
        self.assertEqual(operation.produces, ['application/json'])
        self.assertEqual(operation.path_name, '/pets')

        # Now we check the parameters for the operation
        self.assertEqual(len(operation.params), 1)

        param = operation.params.get('limit')
        self.assertEqual(param.param_spec['required'], False)
        self.assertEqual(param.param_spec['in'], 'query')
        self.assertEqual(param.param_spec['type'], 'integer')
        self.assertEqual(param.fill, None)

        # And check the second one too
        (spec, api_resource_name, resource,
         operation_name, operation, parameters) = data[1]

        self.assertEqual(len(operation.params), 1)

        param = operation.params.get('limit')
        self.assertEqual(param.param_spec['required'], False)
        self.assertEqual(param.param_spec['in'], 'query')
        self.assertEqual(param.param_spec['type'], 'integer')
        self.assertEqual(param.fill, 42)

    def test_simple_int_param_in_path(self):
        specification_as_string = IntParamPath().get_specification()
        http_response = self.generate_response(specification_as_string)
        handler = SpecificationHandler(http_response)

        data = [d for d in handler.get_api_information()]

        self.assertEqual(len(data), 1)

        (spec, api_resource_name, resource,
         operation_name, operation, parameters) = data[0]

        self.assertEqual(api_resource_name, 'pets')
        self.assertEqual(operation_name, 'get_pets_pet_id')
        self.assertEqual(operation.consumes, [])
        self.assertEqual(operation.produces, [])
        self.assertEqual(operation.path_name, '/pets/{pet_id}')

        # And now the real stuff...
        self.assertEqual(len(operation.params), 1)

        param = operation.params.get('pet_id')
        self.assertEqual(param.param_spec['required'], True)
        self.assertEqual(param.param_spec['in'], 'path')
        self.assertEqual(param.param_spec['type'], 'integer')
        self.assertEqual(param.fill, 42)

    def test_simple_string_param_in_qs(self):
        specification_as_string = StringParamQueryString().get_specification()
        http_response = self.generate_response(specification_as_string)
        handler = SpecificationHandler(http_response)

        data = [d for d in handler.get_api_information()]

        # The specification says that this query string parameter is
        # required and there is only one parameter, so there is no second
        # operation with the optional parameters filled in.
        self.assertEqual(len(data), 1)

        (spec, api_resource_name, resource,
         operation_name, operation, parameters) = data[0]

        self.assertEqual(api_resource_name, 'pets')
        self.assertEqual(operation_name, 'findPets')
        self.assertEqual(operation.consumes, ['application/json'])
        self.assertEqual(operation.produces, ['application/json'])
        self.assertEqual(operation.path_name, '/pets')

        # Now we check the parameters for the operation
        self.assertEqual(len(operation.params), 1)

        param = operation.params.get('q')
        self.assertEqual(param.param_spec['required'], True)
        self.assertEqual(param.param_spec['in'], 'query')
        self.assertEqual(param.param_spec['type'], 'string')
        self.assertEqual(param.fill, 'Spam or Eggs?')

    def test_string_param_header(self):
        specification_as_string = StringParamHeader().get_specification()
        http_response = self.generate_response(specification_as_string)
        handler = SpecificationHandler(http_response)

        data = [d for d in handler.get_api_information()]

        # The specification says that this query string parameter is
        # required and there is only one parameter, so there is no second
        # operation with the optional parameters filled in.
        self.assertEqual(len(data), 1)

        (spec, api_resource_name, resource,
         operation_name, operation, parameters) = data[0]

        self.assertEqual(api_resource_name, 'pets')
        self.assertEqual(operation_name, 'findPets')
        self.assertEqual(operation.consumes, ['application/json'])
        self.assertEqual(operation.produces, ['application/json'])
        self.assertEqual(operation.path_name, '/pets')

        # Now we check the parameters for the operation
        self.assertEqual(len(operation.params), 1)

        param = operation.params.get('X-Foo-Header')
        self.assertEqual(param.param_spec['required'], True)
        self.assertEqual(param.param_spec['in'], 'header')
        self.assertEqual(param.param_spec['type'], 'string')
        self.assertEqual(param.fill, '56')

    def test_array_string_items_param_in_qs(self):
        specification_as_string = ArrayStringItemsQueryString().get_specification()
        http_response = self.generate_response(specification_as_string)
        handler = SpecificationHandler(http_response)

        data = [d for d in handler.get_api_information()]

        # The specification says that this query string parameter is
        # required and there is only one parameter, so there is no second
        # operation with the optional parameters filled in.
        self.assertEqual(len(data), 1)

        (spec, api_resource_name, resource,
         operation_name, operation, parameters) = data[0]

        self.assertEqual(api_resource_name, 'pets')
        self.assertEqual(operation_name, 'addTags')
        self.assertEqual(operation.consumes, ['application/json'])
        self.assertEqual(operation.produces, ['application/json'])
        self.assertEqual(operation.path_name, '/pets')

        # Now we check the parameters for the operation
        self.assertEqual(len(operation.params), 1)

        param = operation.params.get('tags')
        self.assertEqual(param.param_spec['required'], True)
        self.assertEqual(param.param_spec['in'], 'query')
        self.assertEqual(param.param_spec['type'], 'array')
        self.assertEqual(param.fill, ['56'])

    def test_array_int_items_param_in_qs(self):
        specification_as_string = ArrayIntItemsQueryString().get_specification()
        http_response = self.generate_response(specification_as_string)
        handler = SpecificationHandler(http_response)

        data = [d for d in handler.get_api_information()]

        # The specification says that this query string parameter is
        # required and there is only one parameter, so there is no second
        # operation with the optional parameters filled in.
        self.assertEqual(len(data), 1)

        (spec, api_resource_name, resource,
         operation_name, operation, parameters) = data[0]

        self.assertEqual(api_resource_name, 'pets')
        self.assertEqual(operation_name, 'addTags')
        self.assertEqual(operation.consumes, ['application/json'])
        self.assertEqual(operation.produces, ['application/json'])
        self.assertEqual(operation.path_name, '/pets')

        # Now we check the parameters for the operation
        self.assertEqual(len(operation.params), 1)

        param = operation.params.get('tags')
        self.assertEqual(param.param_spec['required'], True)
        self.assertEqual(param.param_spec['in'], 'query')
        self.assertEqual(param.param_spec['type'], 'array')
        self.assertEqual(param.fill, [42])

    def test_model_with_int_param_json(self):
        specification_as_string = IntParamJson().get_specification()
        http_response = self.generate_response(specification_as_string)
        handler = SpecificationHandler(http_response)

        data = [d for d in handler.get_api_information()]

        # The specification says that this query string parameter is
        # required and there is only one parameter, so there is no second
        # operation with the optional parameters filled in.
        self.assertEqual(len(data), 1)

        (spec, api_resource_name, resource,
         operation_name, operation, parameters) = data[0]

        self.assertEqual(api_resource_name, 'pets')
        self.assertEqual(operation_name, 'addPet')
        self.assertEqual(operation.consumes, ['application/json'])
        self.assertEqual(operation.produces, ['application/json'])
        self.assertEqual(operation.path_name, '/pets')

        # Now we check the parameters for the operation
        self.assertEqual(len(operation.params), 1)

        param = operation.params.get('pet')
        self.assertEqual(param.param_spec['required'], True)
        self.assertEqual(param.param_spec['in'], 'body')
        self.assertIn('schema', param.param_spec)
        self.assertEqual(param.fill, {'count': 42})

    def test_model_with_string_param_json(self):
        specification_as_string = StringParamJson().get_specification()
        http_response = self.generate_response(specification_as_string)
        handler = SpecificationHandler(http_response)

        data = [d for d in handler.get_api_information()]

        # The specification says that this query string parameter is
        # required and there is only one parameter, so there is no second
        # operation with the optional parameters filled in.
        self.assertEqual(len(data), 1)

        (spec, api_resource_name, resource,
         operation_name, operation, parameters) = data[0]

        self.assertEqual(api_resource_name, 'pets')
        self.assertEqual(operation_name, 'addPet')
        self.assertEqual(operation.consumes, ['application/json'])
        self.assertEqual(operation.produces, ['application/json'])
        self.assertEqual(operation.path_name, '/pets')

        # Now we check the parameters for the operation
        self.assertEqual(len(operation.params), 1)

        param = operation.params.get('pet')
        self.assertEqual(param.param_spec['required'], True)
        self.assertEqual(param.param_spec['in'], 'body')
        self.assertIn('schema', param.param_spec)
        self.assertEqual(param.fill, {'tag': '7', 'name': 'John'})

    def test_no_model_json_object_with_int_param_in_body(self):
        specification_as_string = IntParamNoModelJson().get_specification()
        http_response = self.generate_response(specification_as_string)
        handler = SpecificationHandler(http_response)

        data = [d for d in handler.get_api_information()]

        # The specification says that this query string parameter is
        # required and there is only one parameter, so there is no second
        # operation with the optional parameters filled in.
        self.assertEqual(len(data), 1)

        (spec, api_resource_name, resource,
         operation_name, operation, parameters) = data[0]

        self.assertEqual(api_resource_name, 'pets')
        self.assertEqual(operation_name, 'addPet')
        self.assertEqual(operation.consumes, ['application/json'])
        self.assertEqual(operation.produces, ['application/json'])
        self.assertEqual(operation.path_name, '/pets')

        # Now we check the parameters for the operation
        self.assertEqual(len(operation.params), 1)

        param = operation.params.get('pet')
        self.assertEqual(param.param_spec['required'], True)
        self.assertEqual(param.param_spec['in'], 'body')
        self.assertIn('schema', param.param_spec)
        self.assertEqual(param.fill, {'age': 42, 'name': 'John'})

    def test_no_model_json_object_complex_nested_in_body(self):
        specification_as_string = ComplexDereferencedNestedModel().get_specification()
        http_response = self.generate_response(specification_as_string)
        handler = SpecificationHandler(http_response)

        data = [d for d in handler.get_api_information()]

        # The specification says that this query string parameter is
        # required and there is only one parameter, so there is no second
        # operation with the optional parameters filled in.
        self.assertEqual(len(data), 1)

        (spec, api_resource_name, resource,
         operation_name, operation, parameters) = data[0]

        self.assertEqual(api_resource_name, 'pets')
        self.assertEqual(operation_name, 'post_pets')
        self.assertEqual(operation.consumes, ['application/json'])
        self.assertEqual(operation.produces, ['application/json'])
        self.assertEqual(operation.path_name, '/pets')

        # Now we check the parameters for the operation
        self.assertEqual(len(operation.params), 1)

        param = operation.params.get('pet')
        self.assertEqual(param.param_spec['required'], True)
        self.assertEqual(param.param_spec['in'], 'body')
        self.assertIn('schema', param.param_spec)

        expected_value = {'birthdate': datetime.date(2017, 6, 30),
                          'name': 'John',
                          'owner': {'address': {'city': 'Buenos Aires',
                                                  'postalCode': '90210',
                                                  'state': 'AK',
                                                  'street1': 'Bonsai Street 123',
                                                  'street2': 'Bonsai Street 123'},
                                     'name': {'first': '56', 'last': 'Smith'}},
                          'type': 'cat'}
        self.assertEqual(param.fill, expected_value)

    def test_array_with_model_items_param_in_json(self):
        specification_as_string = ArrayModelItems().get_specification()
        http_response = self.generate_response(specification_as_string)
        handler = SpecificationHandler(http_response)

        data = [d for d in handler.get_api_information()]

        # The specification says that this query string parameter is
        # required and there is only one parameter, so there is no second
        # operation with the optional parameters filled in.
        self.assertEqual(len(data), 1)

        (spec, api_resource_name, resource,
         operation_name, operation, parameters) = data[0]

        self.assertEqual(api_resource_name, 'pets')
        self.assertEqual(operation_name, 'addMultiplePets')
        self.assertEqual(operation.consumes, ['application/json'])
        self.assertEqual(operation.produces, ['application/json'])
        self.assertEqual(operation.path_name, '/pets')

        # Now we check the parameters for the operation
        self.assertEqual(len(operation.params), 1)

        param = operation.params.get('pets')
        self.assertEqual(param.param_spec['required'], True)
        self.assertEqual(param.param_spec['in'], 'body')
        self.assertIn('schema', param.param_spec)

        expected_value = [{'name': 'John', 'tag': '7'}]
        self.assertEqual(param.fill, expected_value)

    def test_model_param_nested_allOf_in_json(self):
        specification_as_string = NestedModel().get_specification()
        http_response = self.generate_response(specification_as_string)
        handler = SpecificationHandler(http_response)

        data = [d for d in handler.get_api_information()]

        self.assertEqual(len(data), 1)

        #
        # Assertions on call #1
        #
        (spec, api_resource_name, resource,
         operation_name, operation, parameters) = data[0]

        self.assertEqual(api_resource_name, 'pets')
        self.assertEqual(operation_name, 'findPets')
        self.assertEqual(operation.consumes, ['application/json'])
        self.assertEqual(operation.produces, ['application/json',
                                              'application/xml',
                                              'text/xml',
                                              'text/html'])
        self.assertEqual(operation.path_name, '/pets')

        # Now we check the parameters for the operation
        self.assertEqual(len(operation.params), 1)

        param = operation.params.get('pet')
        self.assertEqual(param.param_spec['required'], True)
        self.assertEqual(param.param_spec['in'], 'body')
        self.assertIn('schema', param.param_spec)

        expected_value = {'tag': '7', 'name': 'John', 'id': 42}
        self.assertEqual(param.fill, expected_value)

    def test_model_param_nested_loop_in_json(self):
        specification_as_string = NestedLoopModel().get_specification()
        http_response = self.generate_response(specification_as_string)
        handler = SpecificationHandler(http_response)

        data = [d for d in handler.get_api_information()]

        self.assertEqual(len(data), 1, data)

        #
        # Assertions on call #1
        #
        spec, api_resource_name, resource, operation_name, operation, parameters = data[0]

        self.assertEqual(api_resource_name, 'pets')
        self.assertEqual(operation_name, 'findPets')
        self.assertEqual(operation.consumes, ['application/json'])
        self.assertEqual(operation.produces, ['application/json', 'application/xml', 'text/xml', 'text/html'])
        self.assertEqual(operation.path_name, '/pets')

    def test_dereferenced_pet_store(self):
        # See: dereferenced_pet_store.json , which was generated using
        # http://bigstickcarpet.com/swagger-parser/www/index.html#

        specification_as_string = DereferencedPetStore().get_specification()
        http_response = self.generate_response(specification_as_string)
        handler = SpecificationHandler(http_response)

        data = [d for d in handler.get_api_information()]
        self.assertEqual(len(data), 3)

        #
        # Assertions on call #1
        #
        (spec, api_resource_name, resource,
         operation_name, operation, parameters) = data[2]

        self.assertEqual(api_resource_name, 'pets')
        self.assertEqual(operation_name, 'get_pets_name')
        self.assertEqual(operation.consumes, ['application/json'])
        self.assertEqual(operation.produces, ['application/json'])
        self.assertEqual(operation.path_name, '/pets/{name}')

        # Now we check the parameters for the operation
        self.assertEqual(len(operation.params), 1)

        param = operation.params.get('name')
        self.assertEqual(param.param_spec['required'], True)
        self.assertEqual(param.param_spec['in'], 'path')
        self.assertEqual(param.param_spec['type'], 'string')

        expected_value = 'John'
        self.assertEqual(param.fill, expected_value)

        #
        # Assertions on call #2
        #
        (spec, api_resource_name, resource,
         operation_name, operation, parameters) = data[0]

        self.assertEqual(api_resource_name, 'pets')
        self.assertEqual(operation_name, 'get_pets')
        self.assertEqual(operation.consumes, ['application/json'])
        self.assertEqual(operation.produces, ['application/json'])
        self.assertEqual(operation.path_name, '/pets')

        # Now we check the parameters for the operation
        self.assertEqual(len(operation.params), 0)

        #
        # Assertions on call #3
        #

        (spec, api_resource_name, resource,
         operation_name, operation, parameters) = data[1]

        self.assertEqual(api_resource_name, 'pets')
        self.assertEqual(operation_name, 'post_pets')
        self.assertEqual(operation.consumes, ['application/json'])
        self.assertEqual(operation.produces, ['application/json'])
        self.assertEqual(operation.path_name, '/pets')

        # Now we check the parameters for the operation
        self.assertEqual(len(operation.params), 1)

        param = operation.params.get('pet')
        self.assertEqual(param.param_spec['required'], True)
        self.assertEqual(param.param_spec['in'], 'body')
        self.assertIn('schema', param.param_spec)

        expected_value = {'owner': {'name': {'last': 'Smith', 'first': '56'},
                                     'address': {'postalCode': '90210',
                                                  'street1': 'Bonsai Street 123',
                                                  'street2': 'Bonsai Street 123',
                                                  'state': 'AK',
                                                  'city': 'Buenos Aires'}},
                          'type': 'cat', 'name': 'John', 'birthdate': datetime.date(2017, 6, 30)}
        self.assertEqual(param.fill, expected_value)

    def test_parameter_handler_no_params(self):
        specification_as_string = NoParams().get_specification()
        http_response = self.generate_response(specification_as_string)
        handler = SpecificationHandler(http_response)
        self.check_parameter_setting(handler)

    def test_parameter_handler_simple_int_param_in_qs(self):
        specification_as_string = IntParamQueryString().get_specification()
        http_response = self.generate_response(specification_as_string)
        handler = SpecificationHandler(http_response)
        self.check_parameter_setting(handler)

    def test_parameter_handler_array_string_items_param_in_qs(self):
        specification_as_string = ArrayStringItemsQueryString().get_specification()
        http_response = self.generate_response(specification_as_string)
        handler = SpecificationHandler(http_response)
        self.check_parameter_setting(handler)

    def test_parameter_handler_no_model_json_object_complex_nested_in_body(self):
        specification_as_string = ComplexDereferencedNestedModel().get_specification()
        http_response = self.generate_response(specification_as_string)
        handler = SpecificationHandler(http_response)
        self.check_parameter_setting(handler)

    def test_parameter_handler_model_param_nested_allOf_in_json(self):
        specification_as_string = NestedModel().get_specification()
        http_response = self.generate_response(specification_as_string)
        handler = SpecificationHandler(http_response)
        self.check_parameter_setting(handler)

    def test_parameter_handler_multiple_paths_and_headers(self):
        specification_as_string = MultiplePathsAndHeaders().get_specification()
        http_response = self.generate_response(specification_as_string)
        handler = SpecificationHandler(http_response)
        self.check_parameter_setting(handler)

    def check_parameter_setting(self, spec_handler):
        data = [d for d in spec_handler.get_api_information()]
        self.assertIsNotNone(data)
        self.assertIsNotNone(spec_handler.spec)

        for api_resource_name, resource in list(spec_handler.spec.resources.items()):
            for operation_name, operation in list(resource.operations.items()):

                # Make sure that the parameter doesn't have a value yet
                for parameter_name, parameter in operation.params.items():
                    self.assertFalse(hasattr(parameter, 'fill'))

                parameter_handler = ParameterHandler(spec_handler.spec, operation)
                updated_operation = parameter_handler.set_operation_params(True)
                self.assertOperation(operation, updated_operation)

                parameter_handler = ParameterHandler(spec_handler.spec, operation)
                updated_operation = parameter_handler.set_operation_params(False)
                self.assertOperation(operation, updated_operation)

    def assertOperation(self, operation, updated_operation):

        # Make sure that the parameter now has a value
        for parameter_name, parameter in updated_operation.params.items():
            self.assertTrue(hasattr(parameter, 'fill'))

        # Make sure that the original operation doesn't get updated
        # after set_operation_params() call
        self.assertNotEqual(operation, updated_operation)
