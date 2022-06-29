---------- Today's completed jobs by locksmiths 
SELECT
SB.LocksmithName AS "Locksmith",
SB.LocksmithPostCode,
SUM(SB.NetCost) AS NetCost
FROM 
(
SELECT
LD.*,
CK.LocksmithPostCode,
LS.LocksmithName,
PF.NetCost
FROM [dbo].[Policy_LocksmithDetails] LD
LEFT JOIN [dbo].[Lookup_Locksmiths] LS
ON LD.LocksmithID = LS.ID
LEFT JOIN [dbo].[Policy_Financial] PF
ON LD.ReportID = PF.ReportID
LEFT JOIN [dbo].[Policy_ClaimDetails_Key] CK
ON LD.ReportID = CK.ReportID
WHERE LD.Selected = 1
AND LS.LocksmithName LIKE ('WGTK%')
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
GROUP BY SB.LocksmithName , SB.LocksmithPostCode
ORDER BY SUM(SB.NetCost) DESC