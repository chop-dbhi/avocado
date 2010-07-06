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

-- Field Concept

-- create the search_tsv column for fast keyword searching

alter table avocado_fieldconcept add column search_tsv tsvector;

update avocado_fieldconcept U0 set search_tsv = to_tsvector(
    coalesce((select U1.name from avocado_conceptcategory U1 where U0.category_id = U1.id), '') || ' ' ||
    U0.name || ' ' || U0.description || ' ' || U0.keywords);

create index avocado_fieldconcept_search_tsv on avocado_fieldconcept using gin(search_tsv);

create or replace function avocado_fieldconcept_search_tsv_func() returns trigger as $$
    begin
        new.search_tsv :=
            to_tsvector(
            coalesce((select U1.name from avocado_conceptcategory U1 where new.category_id = U1.id), '') || ' '
            || new.name || ' ' || new.description || ' ' || new.keywords);
        return new;
    end
$$ LANGUAGE plpgsql;

create trigger avocado_fieldconcept_search_tsv_update before insert or update
    on avocado_fieldconcept for each row execute procedure avocado_fieldconcept_search_tsv_func();

-- update the search_doc column for icontains searching

update avocado_fieldconcept U0 set search_doc = (coalesce((select U1.name from avocado_conceptcategory U1
    where U0.category_id = U1.id), '') || ' ' || U0.name || ' ' || U0.description || ' ' || U0.keywords);

create or replace function avocado_fieldconcept_search_doc_func() returns trigger as $$
    begin
        new.search_doc :=
        (coalesce((select U1.name from avocado_conceptcategory U1 where new.category_id = U1.id), '') || ' '
            || new.name || ' ' || new.description || ' ' || new.keywords);
        return new;
    end
$$ LANGUAGE plpgsql;

create trigger avocado_fieldconcept_search_doc_update before insert or update
    on avocado_fieldconcept for each row execute procedure avocado_fieldconcept_search_doc_func();

-- Column Concept

-- create the search_tsv column for fast keyword searching

alter table avocado_columnconcept add column search_tsv tsvector;

update avocado_columnconcept U0 set search_tsv = to_tsvector(
    coalesce((select U1.name from avocado_conceptcategory U1 where U0.category_id = U1.id), '') || ' ' ||
    U0.name || ' ' || U0.description || ' ' || U0.keywords);

create index avocado_columnconcept_search_tsv on avocado_columnconcept using gin(search_tsv);

create or replace function avocado_columnconcept_search_tsv_func() returns trigger as $$
    begin
        new.search_tsv :=
            to_tsvector(
            coalesce((select U1.name from avocado_conceptcategory U1 where new.category_id = U1.id), '') || ' '
            || new.name || ' ' || new.description || ' ' || new.keywords);
        return new;
    end
$$ LANGUAGE plpgsql;

create trigger avocado_columnconcept_search_tsv_update before insert or update
    on avocado_columnconcept for each row execute procedure avocado_columnconcept_search_tsv_func();

-- update the search_doc column for icontains searching

update avocado_columnconcept U0 set search_doc = (coalesce((select U1.name from avocado_conceptcategory U1
    where U0.category_id = U1.id), '') || ' ' || U0.name || ' ' || U0.description || ' ' || U0.keywords);

create or replace function avocado_columnconcept_search_doc_func() returns trigger as $$
    begin
        new.search_doc :=
        (coalesce((select U1.name from avocado_conceptcategory U1 where new.category_id = U1.id), '') || ' '
            || new.name || ' ' || new.description || ' ' || new.keywords);
        return new;
    end
$$ LANGUAGE plpgsql;

create trigger avocado_columnconcept_search_doc_update before insert or update
    on avocado_columnconcept for each row execute procedure avocado_columnconcept_search_doc_func();

-- Criterion Concept

-- create the search_tsv column for fast keyword searching

alter table avocado_criterionconcept add column search_tsv tsvector;

update avocado_criterionconcept U0 set search_tsv = to_tsvector(
    coalesce((select U1.name from avocado_conceptcategory U1 where U0.category_id = U1.id), '') || ' ' ||
    U0.name || ' ' || U0.description || ' ' || U0.keywords);

create index avocado_criterionconcept_search_tsv on avocado_criterionconcept using gin(search_tsv);

create or replace function avocado_criterionconcept_search_tsv_func() returns trigger as $$
    begin
        new.search_tsv :=
            to_tsvector(
            coalesce((select U1.name from avocado_conceptcategory U1 where new.category_id = U1.id), '') || ' '
            || new.name || ' ' || new.description || ' ' || new.keywords);
        return new;
    end
$$ LANGUAGE plpgsql;

create trigger avocado_criterionconcept_search_tsv_update before insert or update
    on avocado_criterionconcept for each row execute procedure avocado_criterionconcept_search_tsv_func();

-- update the search_doc column for icontains searching

update avocado_criterionconcept U0 set search_doc = (coalesce((select U1.name from avocado_conceptcategory U1
    where U0.category_id = U1.id), '') || ' ' || U0.name || ' ' || U0.description || ' ' || U0.keywords);

create or replace function avocado_criterionconcept_search_doc_func() returns trigger as $$
    begin
        new.search_doc :=
        (coalesce((select U1.name from avocado_conceptcategory U1 where new.category_id = U1.id), '') || ' '
            || new.name || ' ' || new.description || ' ' || new.keywords);
        return new;
    end
$$ LANGUAGE plpgsql;

create trigger avocado_criterionconcept_search_doc_update before insert or update
    on avocado_criterionconcept for each row execute procedure avocado_criterionconcept_search_doc_func();

commit;
