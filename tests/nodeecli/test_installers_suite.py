import unittest
import sys
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

# Adicionar raiz do projeto ao path para importar os módulos
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from opencode.installer import OpenCodeInstaller
# Antigravity é um script, mas podemos importar funções se ele não executar main() ao importar
# Como ele tem if __name__ == "__main__":, podemos importar, mas ele tenta configurar imports.
# Vamos focar em testar a lógica do OpenCodeInstaller unitariamente
# E testar o GeminiCliInstaller que o script do Antigravity usa.
from nodeecli.modules.gemini_cli_installer import GeminiCliInstaller

class TestOpenCodeInstaller(unittest.TestCase):
    def setUp(self):
        self.installer = OpenCodeInstaller()

    @patch('opencode.installer.requests.get')
    def test_download_success(self, mock_get):
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers.get.return_value = '1024'
        mock_response.iter_content.return_value = [b'x' * 1024]
        mock_get.return_value.__enter__.return_value = mock_response

        # Configurar URL válida (não placeholder)
        self.installer.download_url = "https://valid-url.com/installer.exe"
        
        with patch('opencode.installer.open', mock_open()) as mocked_file, \
             patch('opencode.installer.tempfile.mkstemp', return_value=(1, 'temp_path.exe')), \
             patch('opencode.installer.os.close'):
            
            result = self.installer.download()
            
            self.assertEqual(result, 'temp_path.exe')
            mock_get.assert_called_with("https://valid-url.com/installer.exe", stream=True, timeout=(10, 60))

    def test_download_placeholder(self):
        # Testar comportamento com URL placeholder
        self.installer.download_url = "https://example.com/download/opencode-installer-win64.exe"
        result = self.installer.download()
        self.assertIsNone(result)

    @patch('opencode.installer.subprocess.run')
    @patch('opencode.installer.os.path.exists', return_value=True)
    def test_install_executable(self, mock_exists, mock_run):
        mock_run.return_value.returncode = 0
        
        success = self.installer.install_executable("installer.exe")
        self.assertTrue(success)
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertEqual(args[0], "installer.exe")
        self.assertIn("/S", args)

    def test_verify_checksum(self):
        # Mock file content
        content = b"test content"
        import hashlib
        expected_hash = hashlib.sha256(content).hexdigest()
        
        with patch("builtins.open", mock_open(read_data=content)):
            self.assertTrue(self.installer.verify_checksum("fake_path", expected_hash))
            self.assertFalse(self.installer.verify_checksum("fake_path", "wronghash"))


class TestGeminiCliInstaller(unittest.TestCase):
    def setUp(self):
        self.installer = GeminiCliInstaller()

    @patch('nodeecli.modules.gemini_cli_installer.subprocess.run')
    @patch('nodeecli.modules.gemini_cli_installer.shutil.which')
    def test_verificar_nodejs(self, mock_which, mock_run):
        # Simular node instalado
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "v14.17.0\n"
        
        version = self.installer.verificar_nodejs()
        self.assertEqual(version, "14.17.0")

    @patch('nodeecli.modules.gemini_cli_installer.preparar_ambiente_nodejs')
    @patch('nodeecli.modules.gemini_cli_installer.GeminiCliInstaller.verificar_nodejs')
    @patch('nodeecli.modules.gemini_cli_installer.GeminiCliInstaller.verificar_npm')
    @patch('nodeecli.modules.gemini_cli_installer.subprocess.run')
    def test_instalar_sucesso(self, mock_run, mock_npm, mock_node, mock_prep_env):
        mock_node.return_value = "14.0.0"
        mock_npm.return_value = "C:\\npm.exe"
        mock_prep_env.return_value = {}  # Mock empty environment
        
        # Mock do subprocess.run para instalação
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Success"
        
        # Precisamos também mockar a verificação pós-instalação
        with patch.object(self.installer, 'verificar_gemini_cli') as mock_gemini:
            mock_gemini.return_value = "C:\\gemini.exe"
            
            # Mockar verificação de funcionamento
            mock_run.return_value.returncode = 0 
            mock_run.return_value.stdout = "1.0.0"
            
            success = self.installer.instalar()
            self.assertTrue(success)



if __name__ == '__main__':
    unittest.main()
