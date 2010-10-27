from avocado.conf import settings
from avocado.concepts.managers import ConceptManager

class ColumnManager(ConceptManager):
    def public(self):
        sql = """
        SELECT id
            FROM avocado_column
            WHERE is_public = true
                AND id not IN (
                    SELECT U0.id
                        FROM avocado_column U0
                            INNER JOIN avocado_columnfield U1 ON (U0.id = U1.concept_id)
                            INNER JOIN avocado_field U2 ON (U1.field_id = U2.id)
                        WHERE U2.is_public = false)
        """
        return super(ColumnManager, self).public(sql)

    if settings.FIELD_GROUP_PERMISSIONS:
        def restrict_by_group(self, groups):
            if len(groups) > 0:
                snp = 'AND U2.group_id not in %s'
            else:
                snp = ''

            sql = """
            SELECT id
                FROM avocado_column
                WHERE is_public = true
                    AND id not IN (
                        SELECT U0.id
                            FROM avocado_column U0
                                INNER JOIN avocado_columnfield U1 ON (U0.id = U1.concept_id)
                                INNER JOIN avocado_field U2 ON (U1.field_id = U2.id)
                            WHERE (U2.is_public = false
                                OR (U2.group_id is not NULL %s)))
            """ % snp

            return super(ColumnManager, self).restrict_by_group(sql, groups)

