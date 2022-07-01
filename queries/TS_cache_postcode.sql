------------- Postcode cache in database
SELECT * 
FROM [dbo].[Postcode_coordinates]
WHERE postcode IN ({POSTCODE_LIST});
