import unittest
from unittest.mock import Mock
import kopf
from axop.plugins import InternalPlugin, plugin_from_index, plugins_idx

class TestPlugins(unittest.TestCase):
    
    def setUp(self):
        self._context_name='my-context-name'
        self._plugin_name='data-protection'

        self._plugin_payload="""
        context: '{context}'
        name: io.axoniq.axon-server-plugin-data-protection-azure
        version: '{version}'
        metamodel: '{model}'
        """

        self._plugin_instance_config={    
            'apiVersion':'axoniq.bleuelab.ca/v1',
            'kind':'Plugin',
            'metadata': {
                'name': self._plugin_name
            },
            'spec': {
                'template': {
                    'payload': self._plugin_payload,
                    'variables': ['context','version','model','env']
                }
            }
        }

    def test_plugin_idx_When_valid_config_Should_return_plugin_class(self):
        #Arrange

        #Test
        plugin_idx1=plugins_idx(self._plugin_instance_config).get(self._plugin_name)

        #Assert
        self.assertTrue(isinstance(plugin_idx1, InternalPlugin))

    def test_plugin_from_index_When_two_config_Should_return_last_config(self):
        #Arrange
        plugin_idx1=plugins_idx(self._plugin_instance_config).get(self._plugin_name)
        plugin_idx2=plugins_idx(self._plugin_instance_config).get(self._plugin_name)

        listPlugin:list=[plugin_idx1, plugin_idx2]
        mock_store = Mock(spec=kopf.Store)
        mock_store.__len__ = Mock(return_value=len(listPlugin))
        mock_store.__iter__ = Mock(return_value=iter(listPlugin))
        
        plugins_idx_list:kopf.Index={self._plugin_name: mock_store} 

        #Test
        plugin_instance = plugin_from_index(plugins_idx_list, self._plugin_name)

        #Assert
        self.assertEqual(plugin_instance, plugin_idx2)

    def test_plugin_get_payload_When_model_without_encoding_Should_format_payload_variable(self):
        #Arrange
        plugin_instance_config_model_not_encoded={    
            'apiVersion':'axoniq.bleuelab.ca/v1',
            'kind':'Plugin',
            'metadata': {
                'name': self._plugin_name
            },
            'spec': {
                'template': {
                    'payload': self._plugin_payload,
                    'variables': ['context', 'version', 'model','env']
                }
            }
        }
        plugin_idx1=plugins_idx(plugin_instance_config_model_not_encoded).get(self._plugin_name)

        listPlugin:list=[plugin_idx1]
        mock_store = Mock(spec=kopf.Store)
        mock_store.__len__ = Mock(return_value=len(listPlugin))
        mock_store.__iter__ = Mock(return_value=iter(listPlugin))
        plugins_idx_list:kopf.Index={self._plugin_name: mock_store} 
        plugin_model_not_encoded={
            'env': 'dev',
            'model': '{"config":[{"type":"","revision":"","subjectId":"","sensitiveData":[{"path":"$.person.firstName","replacementValue":null},{"path":"$.person.lastName","replacementValue":null}]}]}',
            'version': '1.0.4'
        }

        plugin_instance = plugin_from_index(plugins_idx_list, self._plugin_name)
        
        #Test
        payload = plugin_instance.get_payload(self._context_name, plugin_model_not_encoded)

        #Assert
        self.assertIsNotNone(payload)
        self.assertEqual(payload['context'], self._context_name)
        self.assertEqual(payload['version'], plugin_model_not_encoded['version'])
        self.assertEqual(payload['metamodel'], plugin_model_not_encoded['model'])

    def test_plugin_get_payload_When_model_encoding_not_encoded_Should_format_payload_variable(self):
        #Arrange
        plugin_instance_config_model_not_encoded={    
            'apiVersion':'axoniq.bleuelab.ca/v1',
            'kind':'Plugin',
            'metadata': {
                'name': self._plugin_name
            },
            'spec': {
                'template': {
                    'payload': self._plugin_payload,
                    'variables': ['context', 'version',{'name':'model','encoding':['']},'env']
                }
            }
        }
        plugin_idx1=plugins_idx(plugin_instance_config_model_not_encoded).get(self._plugin_name)

        listPlugin:list=[plugin_idx1]
        mock_store = Mock(spec=kopf.Store)
        mock_store.__len__ = Mock(return_value=len(listPlugin))
        mock_store.__iter__ = Mock(return_value=iter(listPlugin))
        plugins_idx_list:kopf.Index={self._plugin_name: mock_store} 
        plugin_model_not_encoded={
            'env': 'dev',
            'model': '{"config":[{"type":"","revision":"","subjectId":"","sensitiveData":[{"path":"$.person.firstName","replacementValue":null},{"path":"$.person.lastName","replacementValue":null}]}]}',
            'version': '1.0.4'
        }

        plugin_instance = plugin_from_index(plugins_idx_list, self._plugin_name)
        
        #Test
        payload = plugin_instance.get_payload(self._context_name, plugin_model_not_encoded)

        #Assert
        self.assertIsNotNone(payload)
        self.assertEqual(payload['context'], self._context_name)
        self.assertEqual(payload['version'], plugin_model_not_encoded['version'])
        self.assertEqual(payload['metamodel'], plugin_model_not_encoded['model'])

    def test_plugin_get_payload_When_model_encoded_Should_decode_and_format_payload_variable(self):
        #Arrange
        plugin_instance_config_model_encoded={    
            'apiVersion':'axoniq.bleuelab.ca/v1',
            'kind':'Plugin',
            'metadata': {
                'name': self._plugin_name
            },
            'spec': {
                'template': {
                    'payload': self._plugin_payload,
                    'variables': ['context', 'version',{'name':'model','encoding':['base64:zlib']},'env']
                }
            }
        }
        plugin_idx1=plugins_idx(plugin_instance_config_model_encoded).get(self._plugin_name)
        listPlugin:list=[plugin_idx1]
        mock_store = Mock(spec=kopf.Store)
        mock_store.__len__ = Mock(return_value=len(listPlugin))
        mock_store.__iter__ = Mock(return_value=iter(listPlugin))
        plugins_idx_list:kopf.Index={self._plugin_name: mock_store} 
        plugin_model_encoded={
            'env': 'dev',
            'model': 'eJyrVkrOz0vLTFeyiq5WKqksSFWyUlLSUSpKLcsszszPg/CKS5OyUpNLPFOg3NS84sySzLJUl8SSRLDGgsSSDKCcil5BalFxfp5eWmZRcYlfYm4q2KiCnMTk1NzUvJKwxJxSoAV5pTk5tToYmnISCemJBUIAkY09Lg==',
            'version': '1.0.4'
        }
        
        plugin_instance = plugin_from_index(plugins_idx_list, self._plugin_name)
        
        #Test
        payload = plugin_instance.get_payload(self._context_name, plugin_model_encoded)

        #Assert
        self.assertIsNotNone(payload)
        self.assertEqual(payload['context'], self._context_name)
        self.assertEqual(payload['version'], plugin_model_encoded['version'])
        self.assertEqual(payload['metamodel'], '{"config":[{"type":"","revision":"","subjectId":"","sensitiveData":[{"path":"$.person.firstName","replacementValue":null},"path":"$.person.lastName","replacementValue":null}]}]}')

    def test_plugin_get_payload_When_model_encoding_and_not_encoded_Should_decode_and_format_payload_variable(self):
        #Arrange
        plugin_instance_config_model_encoded={    
            'apiVersion':'axoniq.bleuelab.ca/v1',
            'kind':'Plugin',
            'metadata': {
                'name': self._plugin_name
            },
            'spec': {
                'template': {
                    'payload': self._plugin_payload,
                    'variables': ['context', 'version',{'name':'model','encoding':['base64:zlib','']},'env']
                }
            }
        }
        plugin_idx1=plugins_idx(plugin_instance_config_model_encoded).get(self._plugin_name)
        listPlugin:list=[plugin_idx1]
        mock_store = Mock(spec=kopf.Store)
        mock_store.__len__ = Mock(return_value=len(listPlugin))
        mock_store.__iter__ = Mock(return_value=iter(listPlugin))
        plugins_idx_list:kopf.Index={self._plugin_name: mock_store} 
        plugin_model_encoded={
            'env': 'dev',
            'model': 'eJyrVkrOz0vLTFeyiq5WKqksSFWyUlLSUSpKLcsszszPg/CKS5OyUpNLPFOg3NS84sySzLJUl8SSRLDGgsSSDKCcil5BalFxfp5eWmZRcYlfYm4q2KiCnMTk1NzUvJKwxJxSoAV5pTk5tToYmnISCemJBUIAkY09Lg==',
            'version': '1.0.4'
        }
        
        plugin_instance = plugin_from_index(plugins_idx_list, self._plugin_name)
        
        #Test
        payload = plugin_instance.get_payload(self._context_name, plugin_model_encoded)

        #Assert
        self.assertIsNotNone(payload)
        self.assertEqual(payload['context'], self._context_name)
        self.assertEqual(payload['version'], plugin_model_encoded['version'])
        self.assertEqual(payload['metamodel'], '{"config":[{"type":"","revision":"","subjectId":"","sensitiveData":[{"path":"$.person.firstName","replacementValue":null},"path":"$.person.lastName","replacementValue":null}]}]}')

    def test_plugin_decode_exception_When_model_decoded_throw_Should_print_error(self):
        #Arrange
        plugin_instance_config_model_encoded={    
            'apiVersion':'axoniq.bleuelab.ca/v1',
            'kind':'Plugin',
            'metadata': {
                'name': self._plugin_name
            },
            'spec': {
                'template': {
                    'payload': self._plugin_payload,
                    'variables': ['context', 'version',{'name':'model','encoding':['base64:zlib']},'env']
                }
            }
        }
        plugin_idx1=plugins_idx(plugin_instance_config_model_encoded).get(self._plugin_name)
        listPlugin:list=[plugin_idx1]
        mock_store = Mock(spec=kopf.Store)
        mock_store.__len__ = Mock(return_value=len(listPlugin))
        mock_store.__iter__ = Mock(return_value=iter(listPlugin))
        plugins_idx_list:kopf.Index={self._plugin_name: mock_store} 
        plugin_model_not_encoded={
            'env': 'dev',
            'model': '{"config":[{"type":"","revision":"","subjectId":"","sensitiveData":[{"path":"$.person.firstName","replacementValue":null},"path":"$.person.lastName","replacementValue":null}]}]}',
            'version': '1.0.4'
        }
        
        plugin_instance = plugin_from_index(plugins_idx_list, self._plugin_name)
        
        #Test and Assert value error because decoding throw exception
        with self.assertRaises(ValueError):
            plugin_instance.get_payload(self._context_name, plugin_model_not_encoded)



if __name__ == '__main__':
    unittest.main()