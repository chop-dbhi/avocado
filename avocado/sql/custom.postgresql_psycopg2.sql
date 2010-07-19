-- Custom SQL that defines the necessary triggers for full-text searching for
-- the 'avocado' tables.

-- NOTE: The database must support the 'plpgsql' language. Simply execute the
-- command from the shell:
--
--      $ createlang -d mydb plpgsql
--
-- or from the `psql' command-line:
--
--      mydb=# CREATE LANGUAGE plpgsql;
--

begin;

create language plpgsql;

-- Field Concept

-- create the search_tsv column for fast keyword searching

alter table avocado_modelfield add column search_tsv tsvector;

update avocado_modelfield U0 set search_tsv = to_tsvector(
    coalesce((select U1.name from avocado_category U1 where U0.category_id = U1.id), '') || ' ' ||
    U0.name || ' ' || U0.description || ' ' || U0.keywords);

create index avocado_modelfield_search_tsv on avocado_modelfield using gin(search_tsv);

create or replace function avocado_modelfield_search_tsv_func() returns trigger as $$
    begin
        new.search_tsv :=
            to_tsvector(
            coalesce((select U1.name from avocado_category U1 where new.category_id = U1.id), '') || ' '
            || new.name || ' ' || new.description || ' ' || new.keywords);
        return new;
    end
$$ LANGUAGE plpgsql;

create trigger avocado_modelfield_search_tsv_update before insert or update
    on avocado_modelfield for each row execute procedure avocado_modelfield_search_tsv_func();

-- update the search_doc column for icontains searching

update avocado_modelfield U0 set search_doc = (coalesce((select U1.name from avocado_category U1
    where U0.category_id = U1.id), '') || ' ' || U0.name || ' ' || U0.description || ' ' || U0.keywords);

create or replace function avocado_modelfield_search_doc_func() returns trigger as $$
    begin
        new.search_doc :=
        (coalesce((select U1.name from avocado_category U1 where new.category_id = U1.id), '') || ' '
            || new.name || ' ' || new.description || ' ' || new.keywords);
        return new;
    end
$$ LANGUAGE plpgsql;

create trigger avocado_modelfield_search_doc_update before insert or update
    on avocado_modelfield for each row execute procedure avocado_modelfield_search_doc_func();

-- Column Concept

-- create the search_tsv column for fast keyword searching

alter table avocado_column add column search_tsv tsvector;

update avocado_column U0 set search_tsv = to_tsvector(
    coalesce((select U1.name from avocado_category U1 where U0.category_id = U1.id), '') || ' ' ||
    U0.name || ' ' || U0.description || ' ' || U0.keywords);

create index avocado_column_search_tsv on avocado_column using gin(search_tsv);

create or replace function avocado_column_search_tsv_func() returns trigger as $$
    begin
        new.search_tsv :=
            to_tsvector(
            coalesce((select U1.name from avocado_category U1 where new.category_id = U1.id), '') || ' '
            || new.name || ' ' || new.description || ' ' || new.keywords);
        return new;
    end
$$ LANGUAGE plpgsql;

create trigger avocado_column_search_tsv_update before insert or update
    on avocado_column for each row execute procedure avocado_column_search_tsv_func();

-- update the search_doc column for icontains searching

update avocado_column U0 set search_doc = (coalesce((select U1.name from avocado_category U1
    where U0.category_id = U1.id), '') || ' ' || U0.name || ' ' || U0.description || ' ' || U0.keywords);

create or replace function avocado_column_search_doc_func() returns trigger as $$
    begin
        new.search_doc :=
        (coalesce((select U1.name from avocado_category U1 where new.category_id = U1.id), '') || ' '
            || new.name || ' ' || new.description || ' ' || new.keywords);
        return new;
    end
$$ LANGUAGE plpgsql;

create trigger avocado_column_search_doc_update before insert or update
    on avocado_column for each row execute procedure avocado_column_search_doc_func();

-- Criterion Concept

-- create the search_tsv column for fast keyword searching

alter table avocado_criterion add column search_tsv tsvector;

update avocado_criterion U0 set search_tsv = to_tsvector(
    coalesce((select U1.name from avocado_category U1 where U0.category_id = U1.id), '') || ' ' ||
    U0.name || ' ' || U0.description || ' ' || U0.keywords);

create index avocado_criterion_search_tsv on avocado_criterion using gin(search_tsv);

create or replace function avocado_criterion_search_tsv_func() returns trigger as $$
    begin
        new.search_tsv :=
            to_tsvector(
            coalesce((select U1.name from avocado_category U1 where new.category_id = U1.id), '') || ' '
            || new.name || ' ' || new.description || ' ' || new.keywords);
        return new;
    end
$$ LANGUAGE plpgsql;

create trigger avocado_criterion_search_tsv_update before insert or update
    on avocado_criterion for each row execute procedure avocado_criterion_search_tsv_func();

-- update the search_doc column for icontains searching

update avocado_criterion U0 set search_doc = (coalesce((select U1.name from avocado_category U1
    where U0.category_id = U1.id), '') || ' ' || U0.name || ' ' || U0.description || ' ' || U0.keywords);

create or replace function avocado_criterion_search_doc_func() returns trigger as $$
    begin
        new.search_doc :=
        (coalesce((select U1.name from avocado_category U1 where new.category_id = U1.id), '') || ' '
            || new.name || ' ' || new.description || ' ' || new.keywords);
        return new;
    end
$$ LANGUAGE plpgsql;

create trigger avocado_criterion_search_doc_update before insert or update
    on avocado_criterion for each row execute procedure avocado_criterion_search_doc_func();

commit;
