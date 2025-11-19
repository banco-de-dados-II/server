use bd2;

drop view if exists card;

create view card as
select
    tarefas.id as id, tarefas.status as status, tarefas.titulo as titulo,
    projetos.id as projeto_id,
    projetos.titulo as projeto_nome,
    datas.criacao, datas.fazendo, datas.conclusao, datas.limite,
    pessoas.nome as criador_nome,
    pessoas.id as criador_id,
    tarefas_has_pessoas.tag as tag,
    tarefas_has_pessoas.pessoa_id as atribuido_id
from tarefas
inner join projetos
on tarefas.projeto_id = projetos.id
inner join datas
on tarefas.data_id = datas.id
inner join pessoas
on tarefas.criador_id = pessoas.id
inner join tarefas_has_pessoas
on tarefas.id = tarefas_has_pessoas.tarefa_id ;
