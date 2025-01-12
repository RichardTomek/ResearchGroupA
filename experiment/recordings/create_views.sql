-- Create the cleaned up view of all of the recordings
DROP VIEW IF EXISTS frisbee_view;
CREATE VIEW frisbee_view AS
SELECT
	sd.participant_label as label,
  JSON_EXTRACT(data, '$.heart_rate') as heart_rate,
  JSON_EXTRACT(data, '$.rr_intervals') as rr_intervalls,
  time_recorded,
  "session.code" as session_code,
  current_app_name,
  current_page_name

FROM frisbee_sensor_data sd
JOIN frisbee_otree_context_data cd on sd.otree_context_data_id = cd.id;




-- Create a view to show when each round of the math task started for each participant
DROP VIEW IF EXISTS math_task_rounds;
CREATE VIEW math_task_rounds AS
SELECT
    otp.label,
    mtp.participant_id,
    otp._session_code as session_code,
    mtr.round_number,

    datetime(
			COALESCE(
        LAG(mtr.timestamp) OVER (
            PARTITION BY mtp.participant_id
            ORDER BY mtr.round_number
        ),
        0
    ), 'unixepoch') as round_started_timestamp,
    datetime(mtr.timestamp, 'unixepoch') as round_finished_timestamp
FROM math_task_mathroundresults mtr
    JOIN math_task_player mtp on mtr.player_id = mtp.id
    JOIN otree_participant otp on mtp.participant_id = otp.id;


-- Generate the final view for math task
DROP VIEW IF EXISTS math_task_view;
CREATE VIEW math_task_view AS
SELECT
	fv.label,
  fv.session_code,
  fv.current_app_name,
  mtr.round_number,
  fv.heart_rate,
  fv.rr_intervalls,
  fv.time_recorded
FROM frisbee_view fv
JOIN math_task_rounds mtr ON
	fv.label = mtr.label AND
  fv.session_code = mtr.session_code AND
  (fv.time_recorded >= mtr.round_started_timestamp AND fv.time_recorded <= mtr.round_finished_timestamp)
WHERE current_app_name = 'math_task';


-- Generate round timings for ball task
DROP VIEW IF EXISTS ball_task_rounds;
CREATE VIEW ball_task_rounds AS
SELECT
    otp.label,
    btp.participant_id,
    otp._session_code as session_code,
    btr.round_number,
    datetime(
			COALESCE(
        LAG(btr.timestamp) OVER (
            PARTITION BY btp.participant_id
            ORDER BY btr.round_number
        ),
        0
    ), 'unixepoch') as round_started_timestamp,
    datetime(btr.timestamp, 'unixepoch') as round_finished_timestamp
FROM
	ball_task_ballgameresults btr
JOIN ball_task_player btp on btr.player_id = btp.id
JOIN otree_participant otp on btp.participant_id = otp.id;

-- Final view for the ball task
DROP VIEW IF EXISTS ball_task_view;
CREATE VIEW ball_task_view AS
SELECT
	fv.label,
  fv.session_code,
  fv.current_app_name,
  btr.round_number,
  fv.heart_rate,
  fv.rr_intervalls,
  fv.time_recorded
FROM frisbee_view fv
JOIN ball_task_rounds btr ON
	fv.label = btr.label AND
  fv.session_code = btr.session_code AND
  (fv.time_recorded >= btr.round_started_timestamp AND fv.time_recorded <= btr.round_finished_timestamp)
WHERE current_app_name = 'ball_task';




-- View for the first video task
DROP VIEW IF EXISTS video_one_view;
CREATE VIEW video_one_view AS
SELECT
	fv.label,
  fv.session_code,
  fv.current_app_name,
  fv.heart_rate,
  fv.rr_intervalls,
  fv.time_recorded
FROM frisbee_view fv
WHERE current_app_name = 'video_task_one';


-- View for the second video task
DROP VIEW IF EXISTS video_two_view;
CREATE VIEW video_two_view AS
SELECT
	fv.label,
  fv.session_code,
  fv.current_app_name,
  fv.heart_rate,
  fv.rr_intervalls,
  fv.time_recorded
FROM frisbee_view fv
WHERE current_app_name = 'video_task_two'