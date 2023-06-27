SELECT r.uoSCode UoSCode, u.uoSName UosName, r.prereqUoSCode PrereqUoSCode, u2.uoSName PrereqUoSName, r.enforcedSince
FROM UniDB.Requires r
INNER JOIN UniDB.UnitOfStudy u
ON r.uoSCode = u.uoSCode
INNER JOIN UniDB.UnitOfStudy u2
ON r.prereqUoSCode = u2.uoSCode

SELECT uoSCode, string_agg(prereqUoSCode, ', ') PrereqUoSCode
FROM UniDB.Requires
GROUP BY uoSCode

SELECT uoSCode, COUNT(*) "Number of Prerequires"
FROM UniDB.Requires
GROUP BY uoSCode