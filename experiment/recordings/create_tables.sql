-- Create the base table with all recordings
DROP TABLE IF EXISTS frisbee_base;
CREATE TABLE frisbee_base AS
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

-- Create the math task table
DROP TABLE IF EXISTS math_task_table;
CREATE TABLE math_task_table AS
WITH math_rounds AS (
    SELECT
        otp.label,
        otp._session_code as session_code,
        mtr.round_number,
        datetime(
            COALESCE(
                LAG(mtr.timestamp) OVER (
                    PARTITION BY mtp.participant_id
                    ORDER BY mtr.round_number
                ),
                0
            ), 'unixepoch'
        ) as round_started_timestamp,
        datetime(mtr.timestamp, 'unixepoch') as round_finished_timestamp
    FROM math_task_mathroundresults mtr
    JOIN math_task_player mtp on mtr.player_id = mtp.id
    JOIN otree_participant otp on mtp.participant_id = otp.id
)
SELECT
    fb.label,
    fb.session_code,
    fb.current_app_name,
    mr.round_number,
    fb.heart_rate,
    fb.rr_intervalls,
    fb.time_recorded
FROM frisbee_base fb
JOIN math_rounds mr ON
    fb.label = mr.label AND
    fb.session_code = mr.session_code AND
    (fb.time_recorded >= mr.round_started_timestamp AND fb.time_recorded <= mr.round_finished_timestamp)
WHERE current_app_name = 'math_task';

-- Create the ball task table
DROP TABLE IF EXISTS ball_task_table;
CREATE TABLE ball_task_table AS
WITH ball_rounds AS (
    SELECT
        otp.label,
        otp._session_code as session_code,
        btr.round_number,
        datetime(
            COALESCE(
                LAG(btr.timestamp) OVER (
                    PARTITION BY btp.participant_id
                    ORDER BY btr.round_number
                ),
                0
            ), 'unixepoch'
        ) as round_started_timestamp,
        datetime(btr.timestamp, 'unixepoch') as round_finished_timestamp
    FROM ball_task_ballgameresults btr
    JOIN ball_task_player btp on btr.player_id = btp.id
    JOIN otree_participant otp on btp.participant_id = otp.id
)
SELECT
    fb.label,
    fb.session_code,
    fb.current_app_name,
    br.round_number,
    fb.heart_rate,
    fb.rr_intervalls,
    fb.time_recorded
FROM frisbee_base fb
JOIN ball_rounds br ON
    fb.label = br.label AND
    fb.session_code = br.session_code AND
    (fb.time_recorded >= br.round_started_timestamp AND fb.time_recorded <= br.round_finished_timestamp)
WHERE current_app_name = 'ball_task';

-- Create the first video task table
DROP TABLE IF EXISTS video_one_table;
CREATE TABLE video_one_table AS
SELECT
    label,
    session_code,
    current_app_name,
    heart_rate,
    rr_intervalls,
    time_recorded
FROM frisbee_base
WHERE current_app_name = 'video_task_one';

-- Create the second video task table
DROP TABLE IF EXISTS video_two_table;
CREATE TABLE video_two_table AS
SELECT
    label,
    session_code,
    current_app_name,
    heart_rate,
    rr_intervalls,
    time_recorded
FROM frisbee_base
WHERE current_app_name = 'video_task_two';

-- Create indexes for better query performance
CREATE INDEX idx_math_label_session ON math_task_table(label, session_code);
CREATE INDEX idx_ball_label_session ON ball_task_table(label, session_code);
CREATE INDEX idx_video1_label_session ON video_one_table(label, session_code);
CREATE INDEX idx_video2_label_session ON video_two_table(label, session_code);