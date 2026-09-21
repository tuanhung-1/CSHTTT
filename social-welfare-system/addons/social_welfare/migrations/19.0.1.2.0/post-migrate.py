def migrate(cr, version):
    """Backfill normalized household values without deleting legacy data."""
    cr.execute(
        """
        UPDATE social_household AS household
           SET member_count = (
               SELECT COUNT(*)
                 FROM social_citizen AS citizen
                WHERE citizen.household_id = household.id
           )
        """
    )
    cr.execute(
        """
        UPDATE social_household AS household
           SET head_citizen_id = head.id
          FROM (
              SELECT DISTINCT ON (household_id) id, household_id
                FROM social_citizen
               WHERE relationship = 'head'
               ORDER BY household_id, id
          ) AS head
         WHERE household.id = head.household_id
           AND household.head_citizen_id IS NULL
        """
    )
