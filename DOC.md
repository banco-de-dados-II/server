# templates padrao

rota: string = `nome da rota atual do servidor`
tarefa_status: [string] = `lista de todos os status possiveis para uma tarefa, util para gerar html`
nome: string | null = `nome do usuario`
email: string | null = `email do usuario`

# rotas

## home/
utilizando para debug como por examplo gerar todos os
items do banco de dados

## login/
é possivel logar com o id do usuario apenas
ou colocar um nome e um email para ele criar um novo usuario
ou entrar em um usuario existem


## perfil/
informacoes do usuario

## tarefas/
lista de todas as tarefas do usuario

### template
tarefas: [{
    id: int, 
    status: string,
    titulo: string,
    projeto_id: int,
    projeto_nome: string,
    cricacao: data,
    fazendo: data,
    conclusao: data,
    limite: data,
    criador_nome: string,
    criador_id: int,
    tag: string,
    atribuido_id: id,
}]

## tarefas/<id>
infomacao sobre a tarefa `<id>`


### template
tarefa: {
    id: int, 
    status: string,
    titulo: string,
    projeto_id: int,
    projeto_nome: string,
    cricacao: data,
    fazendo: data,
    conclusao: data,
    limite: data,
    criador_nome: string,
    criador_id: int,
    tag: string,
    atribuido_id: id,
}

## equipes/
lista de todas as equipes do usuario

### template
equipes: [{
    id: int,
    nome: string, 
    projeto: string | null,
    tag: string,
}]

## equipes/<id>
infomacao sobre a equipe `<id>`

### template
equipe: {
    id: int,
    nome: string, 
    projeto: string | null,
    tag: string,
}

## projetos/
lista de todas os projetos do usuario

### template
projetos: [{
    id: int,
    titulo: string,
    cricacao: data,
    fazendo: data,
    conclusao: data,
    limite: data,
}]

## projeto/<id>
infomacao sobre o projeto `<id>`

### template
projeto: {
    id: int,
    titulo: string,
    cricacao: data,
    fazendo: data,
    conclusao: data,
    limite: data,
}
