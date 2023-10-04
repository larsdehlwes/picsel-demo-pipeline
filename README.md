# picsel-demo-pipeline
## Resumo
Nesse desafio configuramos dois S3 buckets, um privado e um com acesso público de leitura. Utilizando uma função Lambda baixamos dados (temperatura 2m acima da superfície e precipitação total) de reanálise meteorológica de uma API pública para guardá-los temporariamente em um dos buckets criados. (Observa se, que nesse processo os credenciais para acessar a API são guardados de forma segura dentro do SecretsManager.) Em seguida, utilizamos um Glue Job para processar os dados e extrair as linhas de contorno das temperatura média e precipitação total de cada dia e as salvamos em formato GeoJSON dentro do segundo S3 bucket. Também mostramos como configurar um AWS Glue Crawler para catalogar arquivos nos formatos .csv, .json, etc...

## Resultados

## Parte 1
A configuração da função Lambda foi bem direta. Escolhi como runtime a versão estável mais recente da Python, a Python 3.11, a qual também utilizo no meu computador pessoal. Pensei bastante em como demonstrar minha capacidade de escrever uma função Lambda e optei por implementar uma função que faz uma requisição a uma API e, em seguida, baixa os dados requeridos para o bucket a ser criado. Para isso, a função lambda precisa de permissões de escrever no bucket em questão.
<table width="100%">
  <tbody>
  <tr>
    <td>Configuramos o papel para a função Lambda:</td>
    <td>A função Lambda tem acesso completo ao serviço S3:</td>
  </tr>
  <tr>
    <td width="50%"><img src="docs/images/IAM_Role_Lambda.png" width=480></td>
    <td width="50%"><img src="docs/images/Lambda_Permissions_S3.png" width=480></td>
  </tr>
  <tr>
    <td>A função Lambda tem permissão de escrever log:</td>
    <td>A função Lambda precisa de acesso ao SecretsManager para descriptografar os credenciais secretos para fazer uma requisição à API. Observe que apenos o segredo relevante é compartilhado com a função: (Criamos a política personalizada ``SecretsManagerReadAccessPicsel'' para isso.)</td>
  </tr>
  <tr>
    <td width="50%"><img src="docs/images/Lambda_Permissions_CloudWatch.png" width=480></td>
    <td width="50%"><img src="docs/images/Lambda_Permissions_SecretsManager.png" width=480></td>
  </tr>
</table>


## Parte 3
### CloudWatch
Utilizei esse serviço para rastrear fontes de erros no momento da implementação do pipeline e depois para monitorar o funcionamento correto do pipeline. Por exemplo, em um primeiro momento não estava claro como incluir bibliotecas de terceiros na função Lambda e no job do Glue. Logar os erros foi essencial para rastrear o que deu errado. Dessa forma consegui resolver os problemas que surgiram de forma célere.
<table width="100%">
  <tbody>
  <tr>
    <td>Página inicial do serviço CloudWatch com alguns indicadores:</td>
    <td>Temos grupos de log para a função Lambda, o job do Glue e o crawler do Glue:</td>
  </tr>
  <tr>
    <td width="50%"><img src="docs/images/CloudWatch_Logs_Dashboard.png" width=480></td>
    <td width="50%"><img src="docs/images/CloudWatch_Log_Groups.png" width=480></td>
  </tr>
  <tr>
    <td>O painel da função Lambda mostra alguma atividade recente:</td>
    <td>Podemos acessar a história de execuções da função Lambda:</td>
  </tr>
  <tr>
    <td width="50%"><img src="docs/images/CloudWatch_Lambda_Dashboard.png" width=480></td>
    <td width="50%"><img src="docs/images/CloudWatch_Lambda_Logs.png" width=480></td>
  </tr>
  <tr>
    <td>Cada execução do job do Glue adiciona um novo arquivo com os outputs:</td>
    <td>E outro arquivo com os erros:</td>
  </tr>
  <tr>
    <td width="50%"><img src="docs/images/CloudWatch_Glue_Output.png" width=480></td>
    <td width="50%"><img src="docs/images/CloudWatch_Glue_Error.png" width=480></td>
  </tr>
</table>

### CloudTrail
<table width="100%">
  <tbody>
  <tr>
    <td>Visitamos a página do serviço CloudTrail:</td>
    <td>Criamos um ``trail'' básico:</td>
  </tr>
  <tr>
    <td width="50%"><img src="docs/images/CloudTrail_LandingPage.png" width=480></td>
    <td width="50%"><img src="docs/images/CloudTrail_CreateTrail.png" width=480></td>
  </tr>
  <tr>
    <td>O painel mostra os incidadores e parte da história de eventos da nossa conta AWS:</td>
    <td>Podemos acessar a história de eventos associados às nossa conta em mais detalhe:</td>
  </tr>
  <tr>
    <td width="50%"><img src="docs/images/CloudTrail_Dashboard.png" width=480></td>
    <td width="50%"><img src="docs/images/CloudTrail_LoggedEvents.png" width=480></td>
  </tr>
</table>
