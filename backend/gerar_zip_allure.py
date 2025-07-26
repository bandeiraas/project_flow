import os
import json
import zipfile
import shutil

# Lista contendo os 10 resultados JSON como strings
allure_data = [
# 1. Teste de Login com Sucesso (Passed)
"""
{
  "uuid": "d9f8c7b3-a2b1-4f6e-8d9a-1b2c3d4e5f6a",
  "historyId": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6",
  "status": "passed",
  "statusDetails": {},
  "stage": "finished",
  "steps": [
    { "name": "Navegar para a página de login", "status": "passed", "stage": "finished", "steps": [], "attachments": [], "parameters": [], "start": 1678886400000, "stop": 1678886401500 },
    { "name": "Preencher email com 'user@example.com'", "status": "passed", "stage": "finished", "steps": [], "attachments": [], "parameters": [], "start": 1678886401501, "stop": 1678886402000 },
    { "name": "Preencher senha", "status": "passed", "stage": "finished", "steps": [], "attachments": [], "parameters": [], "start": 1678886402001, "stop": 1678886402500 },
    { "name": "Clicar no botão de login", "status": "passed", "stage": "finished", "steps": [], "attachments": [], "parameters": [], "start": 1678886402501, "stop": 1678886403500 },
    { "name": "Verificar se o usuário está logado", "status": "passed", "stage": "finished", "steps": [], "attachments": [], "parameters": [], "start": 1678886403501, "stop": 1678886404000 }
  ],
  "attachments": [], "parameters": [],
  "labels": [
    { "name": "epic", "value": "Autenticação" }, { "name": "feature", "value": "Login" },
    { "name": "story", "value": "Login com credenciais válidas" }, { "name": "severity", "value": "critical" },
    { "name": "package", "value": "com.example.tests.auth" }, { "name": "testClass", "value": "LoginTests" },
    { "name": "thread", "value": "main" }
  ],
  "links": [], "name": "testSuccessfulLogin", "fullName": "com.example.tests.auth.LoginTests.testSuccessfulLogin",
  "start": 1678886400000, "stop": 1678886404000
}
""",
# 2. Teste de Login com Senha Inválida (Failed)
"""
{
  "uuid": "e0a9b8c7-d6f5-4e3d-2c1b-a0b9c8d7e6f5",
  "historyId": "f0e1d2c3b4a5f6e7d8c9b0a1f2e3d4c5",
  "status": "failed",
  "statusDetails": { "known": false, "muted": false, "flaky": false, "message": "AssertionError: A mensagem de erro esperada não foi encontrada. Esperado: 'Senha inválida.', Encontrado: ''", "trace": "java.lang.AssertionError: A mensagem de erro esperada não foi encontrada. Esperado: 'Senha inválida.', Encontrado: ''\\n\\tat org.junit.Assert.fail(Assert.java:88)\\n\\tat com.example.tests.auth.LoginTests.testInvalidPasswordLogin(LoginTests.java:45)" },
  "stage": "finished",
  "steps": [
    { "name": "Preencher email com 'user@example.com'", "status": "passed", "stage": "finished", "start": 1678886405000, "stop": 1678886405500 },
    { "name": "Preencher senha com 'senhainvalida'", "status": "passed", "stage": "finished", "start": 1678886405501, "stop": 1678886406000 },
    { "name": "Verificar mensagem de erro", "status": "failed", "stage": "finished", "start": 1678886406001, "stop": 1678886406500 }
  ],
  "attachments": [ { "name": "Screenshot no momento da falha", "source": "a1b2c3d4-e5f6-7g8h-9i0j-k1l2m3n4o5p6-attachment.png", "type": "image/png" } ],
  "parameters": [],
  "labels": [
    { "name": "epic", "value": "Autenticação" }, { "name": "feature", "value": "Login" },
    { "name": "story", "value": "Login com credenciais inválidas" }, { "name": "severity", "value": "critical" }
  ],
  "links": [{ "name": "BUG-123", "url": "https://jira.example.com/browse/BUG-123", "type": "issue" }],
  "name": "testInvalidPasswordLogin", "fullName": "com.example.tests.auth.LoginTests.testInvalidPasswordLogin",
  "start": 1678886405000, "stop": 1678886406500
}
""",
# 3. Teste de Busca de Produto (Broken)
"""
{
  "uuid": "f1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
  "historyId": "b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7",
  "status": "broken",
  "statusDetails": { "known": false, "muted": false, "flaky": false, "message": "org.openqa.selenium.NoSuchElementException: Não foi possível localizar o elemento: //*[@id='search-button-non-existent']", "trace": "org.openqa.selenium.NoSuchElementException: For documentation on this error, please visit: https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#no-such-element-exception\\n\\tat org.openqa.selenium.remote.RemoteWebDriver.findElement(RemoteWebDriver.java:352)\\n\\tat com.example.tests.search.SearchTests.testSearchProduct(SearchTests.java:23)" },
  "stage": "finished",
  "steps": [
    { "name": "Digitar 'Teclado Mecânico' no campo de busca", "status": "passed", "stage": "finished", "start": 1678886407000, "stop": 1678886407500 },
    { "name": "Clicar no botão de busca", "status": "broken", "stage": "finished", "start": 1678886407501, "stop": 1678886408000 }
  ],
  "attachments": [], "parameters": [],
  "labels": [ { "name": "feature", "value": "Busca" }, { "name": "severity", "value": "normal" } ],
  "links": [], "name": "testSearchProduct", "fullName": "com.example.tests.search.SearchTests.testSearchProduct",
  "start": 1678886407000, "stop": 1678886408000
}
""",
# 4. Teste de Funcionalidade Premium (Skipped)
"""
{
  "uuid": "a2b3c4d5-e6f7-4a8b-9c0d-1e2f3a4b5c6d",
  "historyId": "c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8",
  "status": "skipped",
  "statusDetails": { "message": "Teste pulado: A funcionalidade premium não está habilitada neste ambiente de testes.", "trace": "org.junit.AssumptionViolatedException: Teste pulado: A funcionalidade premium não está habilitada neste ambiente de testes.\\n\\tat com.example.tests.premium.PremiumFeatureTest.setup(PremiumFeatureTest.java:15)" },
  "stage": "finished", "steps": [], "attachments": [], "parameters": [],
  "labels": [ { "name": "feature", "value": "Funcionalidades Premium" }, { "name": "severity", "value": "minor" } ],
  "links": [], "name": "testPremiumFeature", "fullName": "com.example.tests.premium.PremiumFeatureTest.testPremiumFeature",
  "start": 1678886409000, "stop": 1678886409001
}
""",
# 5. Adicionar Produto ao Carrinho (Passed)
"""
{
  "uuid": "b3c4d5e6-f7a8-4b9c-0d1e-2f3a4b5c6d7e",
  "historyId": "d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9",
  "status": "passed", "statusDetails": {}, "stage": "finished",
  "steps": [
    { "name": "Buscar pelo produto 'Mouse Gamer'", "status": "passed", "stage": "finished", "start": 1678886410000, "stop": 1678886411000 },
    { "name": "Clicar no primeiro resultado da busca", "status": "passed", "stage": "finished", "start": 1678886411001, "stop": 1678886412000 },
    { "name": "Clicar no botão 'Adicionar ao Carrinho'", "status": "passed", "stage": "finished", "start": 1678886412001, "stop": 1678886412500 },
    { "name": "Verificar se o item 'Mouse Gamer' está no carrinho", "status": "passed", "stage": "finished", "start": 1678886412501, "stop": 1678886413000 }
  ],
  "attachments": [], "parameters": [],
  "labels": [ { "name": "epic", "value": "Jornada de Compra" }, { "name": "feature", "value": "Carrinho de Compras" }, { "name": "severity", "value": "critical" } ],
  "links": [], "name": "testAddProductToCart", "fullName": "com.example.tests.cart.CartTests.testAddProductToCart",
  "start": 1678886410000, "stop": 1678886413000
}
""",
# 6. Teste de Busca Parametrizado (Passed)
"""
{
  "uuid": "c4d5e6f7-a8b9-4c0d-1e2f-3a4b5c6d7e8f",
  "historyId": "e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0",
  "status": "passed", "statusDetails": {}, "stage": "finished",
  "steps": [ { "name": "Verificar se o título da página contém o termo 'Laptop'", "status": "passed", "stage": "finished", "start": 1678886414000, "stop": 1678886414500 } ],
  "attachments": [], "parameters": [ { "name": "Termo de Busca", "value": "Laptop" } ],
  "labels": [ { "name": "feature", "value": "Busca" }, { "name": "story", "value": "Busca parametrizada" }, { "name": "severity", "value": "normal" } ],
  "links": [], "name": "testSearchWithTerm[Laptop]", "fullName": "com.example.tests.search.SearchTests.testSearchWithTerm[Laptop]",
  "start": 1678886414000, "stop": 1678886414500
}
""",
# 7. Teste de Validação do Total do Carrinho (Failed)
"""
{
  "uuid": "d5e6f7a8-b9c0-4d1e-2f3a-4b5c6d7e8f9a",
  "historyId": "f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1",
  "status": "failed",
  "statusDetails": { "known": false, "muted": false, "flaky": true, "message": "AssertionError: O total do carrinho está incorreto. \\nEsperado: 250.50\\nEncontrado: 250.49", "trace": "java.lang.AssertionError: O total do carrinho está incorreto. \\nEsperado: 250.50\\nEncontrado: 250.49\\n\\tat org.junit.Assert.assertEquals(Assert.java:115)\\n\\tat com.example.tests.cart.CartTests.testCartTotal(CartTests.java:82)" },
  "stage": "finished", "steps": [], "attachments": [], "parameters": [],
  "labels": [ { "name": "epic", "value": "Jornada de Compra" }, { "name": "feature", "value": "Carrinho de Compras" }, { "name": "severity", "value": "major" }, { "name": "tag", "value": "flaky" } ],
  "links": [], "name": "testCartTotal", "fullName": "com.example.tests.cart.CartTests.testCartTotal",
  "start": 1678886415000, "stop": 1678886416000
}
""",
# 8. Navegar para a Página de Perfil (Passed)
"""
{
  "uuid": "e6f7a8b9-c0d1-4e2f-3a4b-5c6d7e8f9a0b",
  "historyId": "a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2",
  "status": "passed", "statusDetails": {}, "stage": "finished",
  "steps": [], "attachments": [], "parameters": [],
  "labels": [ { "name": "feature", "value": "Navegação" }, { "name": "story", "value": "Navegação do usuário logado" }, { "name": "severity", "value": "normal" } ],
  "links": [], "name": "testNavigateToProfile", "fullName": "com.example.tests.navigation.NavigationTests.testNavigateToProfile",
  "start": 1678886417000, "stop": 1678886418500
}
""",
# 9. Teste com Erro de Código (Broken)
"""
{
  "uuid": "f7a8b9c0-d1e2-4f3a-4b5c-6d7e8f9a0b1c",
  "historyId": "b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3",
  "status": "broken",
  "statusDetails": { "known": false, "muted": false, "flaky": false, "message": "java.lang.NullPointerException: Não é possível invocar 'com.example.User.getName()' porque 'user' é nulo", "trace": "java.lang.NullPointerException: Cannot invoke \\"com.example.User.getName()\\" because \\"user\\" is null\\n\\tat com.example.tests.profile.ProfileTests.testUpdateProfile(ProfileTests.java:55)" },
  "stage": "finished", "steps": [], "attachments": [], "parameters": [],
  "labels": [ { "name": "feature", "value": "Perfil do Usuário" }, { "name": "severity", "value": "blocker" } ],
  "links": [], "name": "testUpdateProfile", "fullName": "com.example.tests.profile.ProfileTests.testUpdateProfile",
  "start": 1678886419000, "stop": 1678886419200
}
""",
# 10. Teste de Logout (Passed)
"""
{
  "uuid": "a8b9c0d1-e2f3-4a4b-5c6d-7e8f9a0b1c2d",
  "historyId": "c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4",
  "status": "passed", "statusDetails": {}, "stage": "finished",
  "steps": [
    { "name": "Clicar no menu do usuário", "status": "passed", "stage": "finished", "start": 1678886420000, "stop": 1678886420500 },
    { "name": "Clicar no botão 'Sair'", "status": "passed", "stage": "finished", "start": 1678886420501, "stop": 1678886421000 },
    { "name": "Verificar se foi redirecionado para a página de login", "status": "passed", "stage": "finished", "start": 1678886421001, "stop": 1678886421800 }
  ],
  "attachments": [], "parameters": [],
  "labels": [ { "name": "epic", "value": "Autenticação" }, { "name": "feature", "value": "Logout" }, { "name": "severity", "value": "critical" } ],
  "links": [], "name": "testSuccessfulLogout", "fullName": "com.example.tests.auth.LoginTests.testSuccessfulLogout",
  "start": 1678886420000, "stop": 1678886421800
}
"""
]

def create_allure_zip():
    """Cria os arquivos JSON e os compacta em um arquivo ZIP."""
    temp_dir = 'allure-results-temp'
    zip_filename = 'allure-results-mock2.zip'

    # Limpa execuções anteriores se existirem
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    if os.path.exists(zip_filename):
        os.remove(zip_filename)

    os.makedirs(temp_dir)
    
    print(f"Criando arquivos JSON na pasta temporária '{temp_dir}'...")

    try:
        # Itera sobre os dados JSON e cria os arquivos
        for json_string in allure_data:
            data = json.loads(json_string)
            uuid = data.get('uuid')
            if not uuid:
                print("Aviso: JSON sem UUID encontrado, pulando.")
                continue
            
            # Nome do arquivo no padrão Allure
            filename = f"{uuid}-result.json"
            filepath = os.path.join(temp_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(json_string.strip())
        
        print("Arquivos JSON criados com sucesso.")
        print(f"Criando arquivo ZIP '{zip_filename}'...")

        # Cria o arquivo ZIP
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    filepath = os.path.join(root, file)
                    # Adiciona o arquivo ao ZIP sem o caminho do diretório temporário
                    zipf.write(filepath, arcname=file)
        
        print("-" * 30)
        print(f"SUCESSO! O arquivo '{zip_filename}' foi criado.")
        print("-" * 30)

    finally:
        # Limpa a pasta temporária
        print("Limpando arquivos temporários...")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        print("Limpeza concluída.")


if __name__ == "__main__":
    create_allure_zip()