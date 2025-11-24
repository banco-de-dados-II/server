use bd2;

drop view if exists card;
drop view if exists equipe_full;

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

create view equipe_full as
select
    equipes.id as equipe_id,
    projetos.id as projeto_id,
    pessoas.id as pessoa_id,
    equipes.nome as equipe_nome,
    projetos.titulo as projeto_titulo,
    equipes_has_pessoas.tag as equipe_tag
    from equipes
inner join equipes_has_pessoas on equipes_has_pessoas.equipe_id = equipes.id
inner join pessoas on pessoas.id = equipes_has_pessoas.pessoa_id
inner join projetos_has_equipes on projetos_has_equipes.equipe_id = equipes.id
inner join projetos on projetos.id = projetos_has_equipes.projeto_id ;
