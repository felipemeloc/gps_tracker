------------- Today's jobs/revenue by locksmiths (POSTCODE)
SELECT
SB.RecipientName AS "Locksmith",
SB.LocksmithPostCode,
SB.LocksmithSuppliedServicesIds,
SB.ReportID
FROM 
(
SELECT
LD.*,
CK.LocksmithPostCode,
PF.RecipientName,
PF.NetCost
FROM [dbo].[Policy_LocksmithDetails] LD
LEFT JOIN [dbo].[Policy_Financial] PF
ON LD.ReportID = PF.ReportID
LEFT JOIN [dbo].[Policy_ClaimDetails_Key] CK
ON LD.ReportID = CK.ReportID
WHERE LD.Selected = 1
AND PF.RecipientName LIKE ('WGTK%')
AND LD.ReportID IN (
	SELECT
	DISTINCT(PD.ReportID)
	FROM
	[dbo].[Policy_Diary] PD
	WHERE PD.Active = 0
	AND CAST(PD.ClosedDate AS DATE) > DATEADD(DAY, -2, GETDATE())
)
AND CAST(LD.AvailableFromDate AS DATE) > DATEADD(DAY, -2, GETDATE())
) AS SB
WHERE SB.NetCost IS NOT NULL
GROUP BY SB.RecipientName, SB.LocksmithPostCode, SB.LocksmithSuppliedServicesIds, SB.ReportID;