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

-- There is no OR REPLACE or IF NOT EXISTS for CREATE LANGUAGE, so this
-- must be setup ahead of time. Attempting to create the language causes
-- an error.
-- create language plpgsql;

-- Field Concept

-- create the search_tsv column for fast keyword searching

alter table avocado_field add column search_tsv tsvector;

update avocado_field U0 set search_tsv = to_tsvector(
    coalesce(U0.name, '') || ' ' ||
    coalesce(U0.description, '') || ' ' ||
    coalesce(U0.keywords, ''));

create index avocado_field_search_tsv on avocado_field using gin(search_tsv);

create or replace function avocado_field_search_tsv_func() returns trigger as $$
    begin
        new.search_tsv := to_tsvector(
            coalesce(new.name, '') || ' ' ||
            coalesce(new.description, '') || ' ' ||
            coalesce(new.keywords, ''));
        return new;
    end
$$ LANGUAGE plpgsql;

create trigger avocado_field_search_tsv_update before insert or update
    on avocado_field for each row execute procedure avocado_field_search_tsv_func();

-- update the search_doc column for icontains searching

update avocado_field U0 set search_doc = (
    coalesce(U0.name, '') || ' ' ||
    coalesce(U0.description, '') || ' ' ||
    coalesce(U0.keywords, ''));

create or replace function avocado_field_search_doc_func() returns trigger as $$
    begin
        new.search_doc := (
            coalesce(new.name, '') || ' ' ||
            coalesce(new.description, '') || ' ' ||
            coalesce(new.keywords, ''));
        return new;
    end
$$ LANGUAGE plpgsql;

create trigger avocado_field_search_doc_update before insert or update
    on avocado_field for each row execute procedure avocado_field_search_doc_func();



-- Column Concept

-- create the search_tsv column for fast keyword searching

alter table avocado_column add column search_tsv tsvector;

update avocado_column U0 set search_tsv = to_tsvector(
    coalesce((select U1.name from avocado_category U1 where U0.category_id = U1.id), '') || ' ' ||
    coalesce(U0.name, '') || ' ' ||
    coalesce(U0.description, '') || ' ' ||
    coalesce(U0.keywords, ''));

create index avocado_column_search_tsv on avocado_column using gin(search_tsv);

create or replace function avocado_column_search_tsv_func() returns trigger as $$
    begin
        new.search_tsv := to_tsvector(
            coalesce((select U1.name from avocado_category U1 where new.category_id = U1.id), '') || ' ' ||
            coalesce(new.name, '') || ' ' ||
            coalesce(new.description, '') || ' ' ||
            coalesce(new.keywords, ''));
        return new;
    end
$$ LANGUAGE plpgsql;

create trigger avocado_column_search_tsv_update before insert or update
    on avocado_column for each row execute procedure avocado_column_search_tsv_func();

-- update the search_doc column for icontains searching

update avocado_column U0 set search_doc = (
    coalesce((select U1.name from avocado_category U1 where U0.category_id = U1.id), '') || ' ' ||
    coalesce(U0.name, '') || ' ' ||
    coalesce(U0.description, '') || ' ' ||
    coalesce(U0.keywords, ''));

create or replace function avocado_column_search_doc_func() returns trigger as $$
    begin
        new.search_doc := (
            coalesce((select U1.name from avocado_category U1 where new.category_id = U1.id), '') || ' ' ||
            coalesce(new.name, '') || ' ' ||
            coalesce(new.description, '') || ' ' ||
            coalesce(new.keywords, ''));
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
    coalesce(U0.name, '') || ' ' ||
    coalesce(U0.description, '') || ' ' ||
    coalesce(U0.keywords, ''));

create index avocado_criterion_search_tsv on avocado_criterion using gin(search_tsv);

create or replace function avocado_criterion_search_tsv_func() returns trigger as $$
    begin
        new.search_tsv := to_tsvector(
            coalesce((select U1.name from avocado_category U1 where new.category_id = U1.id), '') || ' ' ||
            coalesce(new.name, '') || ' ' ||
            coalesce(new.description, '') || ' ' ||
            coalesce(new.keywords, ''));
        return new;
    end
$$ LANGUAGE plpgsql;

create trigger avocado_criterion_search_tsv_update before insert or update
    on avocado_criterion for each row execute procedure avocado_criterion_search_tsv_func();

-- update the search_doc column for icontains searching

update avocado_criterion U0 set search_doc = (
    coalesce((select U1.name from avocado_category U1 where U0.category_id = U1.id), '') || ' ' ||
    coalesce(U0.name, '') || ' ' ||
    coalesce(U0.description, '') || ' ' ||
    coalesce(U0.keywords, ''));

create or replace function avocado_criterion_search_doc_func() returns trigger as $$
    begin
        new.search_doc := (
            coalesce((select U1.name from avocado_category U1 where new.category_id = U1.id), '') || ' ' ||
            coalesce(new.name, '') || ' ' ||
            coalesce(new.description, '') || ' ' ||
            coalesce(new.keywords, ''));
        return new;
    end
$$ LANGUAGE plpgsql;

create trigger avocado_criterion_search_doc_update before insert or update
    on avocado_criterion for each row execute procedure avocado_criterion_search_doc_func();

commit;
