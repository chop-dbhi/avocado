from avocado.conf import settings
from avocado.concepts.managers import ConceptManager

class CriterionManager(ConceptManager):
    def public(self):
        sql = """
        SELECT id
            FROM avocado_criterion
            WHERE is_public = true
                AND id not IN (
                    SELECT U0.id
                        FROM avocado_criterion U0
                            INNER JOIN avocado_criterionfield U1 ON (U0.id = U1.concept_id)
                            INNER JOIN avocado_field U2 ON (U1.field_id = U2.id)
                        WHERE U2.is_public = false)
        """
        return super(CriterionManager, self).public(sql)

    if settings.FIELD_GROUP_PERMISSIONS:
        def restrict_by_group(self, groups):
            if len(groups) > 0:
                snp = 'AND U2.group_id not in %s'
            else:
                snp = ''

            sql = """
            SELECT id
                FROM avocado_criterion
                WHERE is_public = true
                    AND id not IN (
                        SELECT U0.id
                            FROM avocado_criterion U0
                                INNER JOIN avocado_criterionfield U1 ON (U0.id = U1.concept_id)
                                INNER JOIN avocado_field U2 ON (U1.field_id = U2.id)
                            WHERE (U2.is_public = false
                                OR (U2.group_id is not NULL %s)))
            """ % snp

            return super(CriterionManager, self).restrict_by_group(sql, groups)

