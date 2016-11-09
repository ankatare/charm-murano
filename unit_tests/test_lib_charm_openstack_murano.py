# Copyright 2016 Canonical Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import
from __future__ import print_function

import contextlib
import unittest

import mock

import charm.openstack.murano as murano


def FakeConfig(init_dict):

    def _config(key=None):
        return init_dict[key] if key else init_dict

    return _config


class Helper(unittest.TestCase):

    def setUp(self):
        self._patches = {}
        self._patches_start = {}
        self.ch_config_patch = mock.patch('charmhelpers.core.hookenv.config')
        self.ch_config = self.ch_config_patch.start()
        self.ch_config.side_effect = lambda: {'ssl_param': None}

    def tearDown(self):
        for k, v in self._patches.items():
            v.stop()
            setattr(self, k, None)
        self._patches = None
        self._patches_start = None
        self.ch_config_patch.stop()

    def patch(self, obj, attr, return_value=None, **kwargs):
        mocked = mock.patch.object(obj, attr, **kwargs)
        self._patches[attr] = mocked
        started = mocked.start()
        started.return_value = return_value
        self._patches_start[attr] = started
        setattr(self, attr, started)

    def patch_object(self, obj, attr, return_value=None, name=None, new=None):
        if name is None:
            name = attr
        if new is not None:
            mocked = mock.patch.object(obj, attr, new=new)
        else:
            mocked = mock.patch.object(obj, attr)
        self._patches[name] = mocked
        started = mocked.start()
        if new is None:
            started.return_value = return_value
        self._patches_start[name] = started
        setattr(self, name, started)


class TestOpenStackMurano(Helper):


    def test_register_endpoints(self):
        self.patch(murano.MuranoCharm, 'service_type',
                   new_callable=mock.PropertyMock)
        self.patch(murano.MuranoCharm, 'region',
                   new_callable=mock.PropertyMock)
        self.patch(murano.MuranoCharm, 'public_url',
                   new_callable=mock.PropertyMock)
        self.patch(murano.MuranoCharm, 'internal_url',
                   new_callable=mock.PropertyMock)
        self.patch(murano.MuranoCharm, 'admin_url',
                   new_callable=mock.PropertyMock)
        self.service_type.return_value = 'type1'
        self.region.return_value = 'region1'
        self.public_url.return_value = 'public_url'
        self.internal_url.return_value = 'internal_url'
        self.admin_url.return_value = 'admin_url'
        keystone = mock.MagicMock()
        murano.register_endpoints(keystone)
        keystone.register_endpoints.assert_called_once_with(
            'type1', 'region1', 'public_url', 'internal_url', 'admin_url')

    def test_restart_all(self):
        self.patch(murano.MuranoCharm.singleton, 'restart_all')
        murano.restart_all()
        self.restart_all.assert_called_once_with()

    def test_configure_ssl(self):
        self.patch(murano.MuranoCharm.singleton, 'configure_ssl')
        murano.configure_ssl()
        self.configure_ssl.assert_called_once_with(None)

    def test_update_peers(self):
        self.patch(murano.MuranoCharm.singleton, 'update_peers')
        murano.update_peers('cluster')
        self.update_peers.assert_called_once_with('cluster')

    def test_assess_status(self):
        self.patch(murano.MuranoCharm, 'assess_status')
        murano.assess_status()
        self.assess_status.assert_called_once_with()

    def test_configure_ha_resources(self):
        self.patch(murano.MuranoCharm.singleton, 'db_sync')
        murano.db_sync()
        self.db_sync.assert_called_once_with()
  
    def test_render_novarc_config(self):
        self.patch(murano.MuranoCharm.singleton, 'render_novarc_config')
        murano.render_novarc_config('interfaces_list')
        self.render_novarc_config.assert_called_once_with('interfaces_list')


class TestMuranoCharm(Helper):

    def test_install(self):
        self.patch(murano.MuranoCharm, 'configure_source')
        a = murano.MuranoCharm(release='mitaka')
        a.install()
        self.configure_source.assert_called_with()

    def test__init__(self):
        self.patch(murano.MuranoCharm,
                   'set_config_defined_certs_and_keys')
        self.patch(murano.ch_utils, 'os_release')
        murano.MuranoCharm()
        self.os_release.assert_called_once_with('python-keystonemiddleware')


    def test_io_murano(self):
        self.patch(murano.MuranoCharm,
                   'set_config_defined_certs_and_keys')
        self.patch(murano.ch_utils, 'os_release')
        b=murano.MuranoCharm()
        b.import_io_murano()
        self.os_release.assert_called_once_with('python-keystonemiddleware')

