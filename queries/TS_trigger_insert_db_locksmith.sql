------------- Trigger before insert into the gps rodean table
CREATE OR ALTER TRIGGER update_rodean_locksmith ON [dbo].[gps_roedan_locksmith]
	INSTEAD OF INSERT
	AS
	BEGIN
	DROP TABLE IF EXISTS #TempRoedam;
	SELECT * INTO #TempRoedam FROM INSERTED;

	DELETE FROM [dbo].[gps_roedan_locksmith]
	WHERE Route_ID IN (
		SELECT DISTINCT(gs.Route_ID)
		FROM [dbo].[gps_roedan_locksmith] gs
		INNER JOIN #TempRoedam tm
		ON gs.Route_ID = tm.Route_ID
		WHERE gs.Route_ID = tm.Route_ID
	) ;

	INSERT INTO [dbo].[gps_roedan_locksmith]
	SELECT * FROM #TempRoedam;
	
	END
GO