drop trigger if exists avocado_fieldconcept_search_tsv_update on avocado_fieldconcept;
drop trigger if exists avocado_fieldconcept_search_doc_update on avocado_fieldconcept;
drop function if exists avocado_fieldconcept_search_tsv_func();
drop function if exists avocado_fieldconcept_search_doc_func();

-- create the search_tsv column for fast keyword searching

alter table avocado_fieldconcept add column search_tsv tsvector;

update avocado_fieldconcept U0 set search_tsv = to_tsvector(
    coalesce((select U1.name from avocado_conceptcategory U1 where U0.category_id = U1.id), '') || ' ' ||
    U0.name || ' ' || U0.description || ' ' || U0.keywords);

create index avocado_fieldconcept_search_tsv on avocado_fieldconcept using gin(search_tsv);

create function avocado_fieldconcept_search_tsv_func() returns trigger as $$
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

create function avocado_fieldconcept_search_doc_func() returns trigger as $$
    begin
        new.search_doc :=
        (coalesce((select U1.name from avocado_conceptcategory U1 where new.category_id = U1.id), '') || ' '
            || new.name || ' ' || new.description || ' ' || new.keywords);
        return new;
    end
$$ LANGUAGE plpgsql;

create trigger avocado_fieldconcept_search_doc_update before insert or update
    on avocado_fieldconcept for each row execute procedure avocado_fieldconcept_search_doc_func();