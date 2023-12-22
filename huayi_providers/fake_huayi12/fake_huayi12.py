import os
from qiskit.providers.fake_provider import fake_qasm_backend, fake_backend

class FakeHuayi12(fake_qasm_backend.FakeQasmBackend):
	dirname = os.path.dirname(__file__)
	conf_filename = 'conf_huayi12.json'
	props_filename = 'props_huayi12.json'
	backend_name = 'fake_huayi12'

class FakeHuayi12V2(fake_backend.FakeBackendV2):
	dirname = os.path.dirname(__file__)
	conf_filename = 'conf_huayi12.json'
	props_filename = 'props_huayi12.json'
	backend_name = 'fake_huayi12'
