------------- Today's jobs/revenue by locksmiths (POSTCODE)
SELECT
SB.RecipientName AS "Locksmith",
SB.LocksmithPostCode,
SB.LocksmithSuppliedServicesIds,
SB.Make AS "CarBrand",
SB.Model AS "CarModel",
SB.yearOfManufacture AS "CarYear",
SB.ReportID
FROM 
(
SELECT
DISTINCT(LD.ReportID),
LD.LocksmithSuppliedServicesIds,
CK.LocksmithPostCode,
PF.RecipientName,
PF.NetCost,
KC.Make,
KC.Model,
KC.yearOfManufacture
FROM [dbo].[Policy_LocksmithDetails] LD
LEFT JOIN [dbo].[Policy_Financial] PF
ON LD.ReportID = PF.ReportID
LEFT JOIN [dbo].[Policy_ClaimDetails_Key] CK
ON LD.ReportID = CK.ReportID
LEFT JOIN [dbo].[Policy_KeyClaims] KC
ON LD.ReportID = KC.ReportID
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
GROUP BY SB.RecipientName, SB.LocksmithPostCode, SB.LocksmithSuppliedServicesIds, SB.Make, SB.Model, SB.yearOfManufacture, SB.ReportID;