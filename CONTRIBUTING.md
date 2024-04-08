# 🌽 Contribuindo com o Code Helper

O objetivo desse projeto e auxiliar na moderação da comunidade [**Code Help**](https://discord.gg/code-help), e agora também pode ajudar você com suas primeiras contribuições com um projeto open-source.

## 1. Faça um Fork deste repositório
Ao fazer um "Fork" deste projeto você faz uma cópia dele para seu própria conta do github, para fazer isso clique no botão **Fork** no topo da página dessa página.

## 2. Clone o repositório
Agora clone este repositório para sua máquina, para ter acesso ao código localmente. Clique no botão **Code** e, em seguida, clique no ícone **Copy to clipboard**, para copiar a URL do projeto.

Abra um terminal e execute o seguite comando do git:
````bash
git clone "url copiada"

``````
Onde a "url copiada" (sem as aspas) é a URL deste repositório (seu fork deste projeto).

Por exemplo:
````bash
git clone https://github.com/seu-usuário/code_helper_py
``````
Onde "seu usuário" é o seu usuário do Github. Aqui você estará copiando conteúdo do repositório *code_helper_py* para sua máquina.

## 3. Crie uma Branch
Acesse o diretório do repositório no seu computador (caso você esteja nele);
````bash
cd code_helper_py
``````
Agora crie uma nova Branch usando o comando `git checkout`:
````bash
git checkout -b feature-<nome-da-nova-feature>
``````
Por exemplo:
````bash
git checkout -b feature-message-automod
``````
Obs.: O nome da Branch deve ser bem descritivo e resumir bem em poucas palavras qual é o intuito de todas as alterações que você fez nela.


## 4. Faça as alterações necessárias e faça um Commit
Agora, sinta-se livre para fazer as modificações que quiser, mas lembre-se que, sua branch deve apenas ter uma finalidade. Por exemplo, se você está adicionando um novo comando, que mostra informações de um usuário, não faz sentido ter modificações em sua Branch em arquivos como os do banco de dados. Lembre-se também de sempre usar os padrão de estilo de código definido pelo Python além de boas práticas de programção.

Se você for ao diretório do projeto, e executar o comando `git status`, verá que há alterações. Adicione essas alterações ao Branch que você acabou de criar utilizando o comando `git add`:
````bash
git add <nome-do-arquivo>
``````
Agora, você como finalmente confirmar essa ação usando o comando `git commit`:
````bash
git commit -m "feat: <titulo do commit>"
``````
Obs.: Assim como a Branch, seus commits devem ter uma descrição bem auto-descritivas e seu conteúdo deve ser atômico. Commit Atômico? Oque é isso? Seus commits devem ser auto-suficientes, ou seja, conter todas as modificações necessárias para que oque foi descrito no título do commit funcione.


## 5. Faça um Push das alterações para o Github
Envie suas alterações usando o commando `git push`:
`````bash
git push origin <nome-da-sua-branch>
`````````
Substituindo `<nome-da-sua-branch>` pelo nome da Branch qeu você criou anteriormente.

## 6. Envia suas alterações para serem revisadas
Se você for para o seu repositório no Github, verá um botão, `Compare $ pull request`, logo abaixo do título do repositório. Clique nesse botão.
Agora, envie um Pull Request, clicando no botão `Create pull request`, no canto inferior direito.

Iremos revisar seu código, e caso faça sentido as alterações, estaremos mesclando (mergeando) as suas mudanças no Branch principal (main) deste projeto. Você receberá um e-mail de notificação quando as alterações forem mescadas.

## Nomenclatura
Use os prefixos abaixo em suas branchs e commits. Caso seus commits não estejam seguindo os padrões de nomenclatura do projeto, serão recusados.

- **feature:** Usado para indicar adicição, atualição e novas funcionalidades no geral.
- **fix:** Usado para correção de bugs e mál funcionameto no geral.

Por exemplo:
````bash
git commit -m "feat: add user info command"
git commit -m "fix: user info command not showing user's avatar"
git checkout -b feature-warnings-system
git checkout -b fix-warning-system-database-connection
``````
