use bd2;

create or replace view card as
select
    tarefas.id as id, tarefas.status as status, tarefas.titulo as titulo,
    projetos.titulo as projeto_nome,
    datas.criacao, datas.fazendo, datas.conclusao, datas.limite,
    pessoas.nome as criador_nome
from tarefas
inner join projetos
on tarefas.projeto_id = projetos.id
inner join datas
on tarefas.data_id = datas.id
inner join pessoas
on tarefas.criador_id = pessoas.id ;
