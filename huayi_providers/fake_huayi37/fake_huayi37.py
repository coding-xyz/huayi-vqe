import os
from qiskit.providers.fake_provider import fake_qasm_backend, fake_backend

class FakeHuayi37(fake_qasm_backend.FakeQasmBackend):
	dirname = os.path.dirname(__file__)
	conf_filename = 'conf_huayi37.json'
	props_filename = 'props_huayi37.json'
	backend_name = 'fake_huayi37'

class FakeHuayi37V2(fake_backend.FakeBackendV2):
	dirname = os.path.dirname(__file__)
	conf_filename = 'conf_huayi37.json'
	props_filename = 'props_huayi37.json'
	backend_name = 'fake_huayi37'
