------------- Today's jobs/revenue by locksmiths 
SELECT
SB.RecipientName AS "Locksmith",
COUNT(*) AS "Jobs",
SUM(SB.NetCost) AS "Revenue"
FROM 
(
SELECT
DISTINCT(LD.ReportID),
PF.RecipientName,
PF.NetCost
FROM [dbo].[Policy_LocksmithDetails] LD
LEFT JOIN [dbo].[Policy_Financial] PF
ON LD.ReportID = PF.ReportID
WHERE LD.Selected = 1
AND PF.RecipientName LIKE ('WGTK%')
AND LD.ReportID IN (
	SELECT
	DISTINCT(PD.ReportID)
	FROM
	[dbo].[Policy_Diary] PD
	WHERE PD.Active = 0
	AND CAST(PD.ClosedDate AS DATE) = CAST(GETDATE() AS DATE)
)
AND CAST(LD.AvailableFromDate AS DATE) = CAST(GETDATE() AS DATE)
) AS SB
WHERE SB.NetCost IS NOT NULL
GROUP BY SB.RecipientName
ORDER BY  SB.RecipientName