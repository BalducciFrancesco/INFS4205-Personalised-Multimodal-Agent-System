Title: Anonymized User Watch Log Dataset
File: youtube_watch_log.csv

Description:
-------------
This dataset contains anonymized logs of user-level video watch activity. Each row represents a single viewing event, with associated metadata such as the video watched, whether the user was subscribed, and whether the video was part of a playlist.

Field Descriptions:
-------------------
- log_id:
  A unique identifier for each watch event.

- user_id:
  An anonymized numeric ID assigned to each user. These are sequential and do not correspond to any personally identifiable information.

- video_id:
  A unique identifier for the video that was watched. This can be used to link with metadata. The `video_id` field can be used to construct a YouTube video URL using:
    https://www.youtube.com/watch?v=VIDEO_ID (Replace `VIDEO_ID` with the value from the `video_id` column)

- watch_date:
  The date and time when the viewing event occurred, formatted as YYYY-MM-DD HH:MM:SS.

- subscribed:
  Indicates whether the user was subscribed to the channel at the time of viewing. Typical values are 'Y' (for yes) or 'N' (for no).

- playlist_name:
  Name of the playlist the video was part of, if applicable. This field have the value "NA" for standalone views.

Summary Statistics:
-------------------
- Total watch events: 1,844,919
- Unique users: 244
- Unique videos: 1,172,110
- Date range: 2010-08-08 to 2018-09-26

Notes:
------
- All user identifiers have been anonymized.
- No personally identifiable information (PII) is included.
- The data is intended for research and analysis purposes only.

  Citation:
  ---------
  If you use this dataset in your research or projects, please cite the following paper:

  S. Lall, M. Agarwal and R. Sivakumar, "A YouTube dataset with user-level usage data: Baseline characteristics and key insights," ICC 2020 - 2020 IEEE International Conference on Communications (ICC), Dublin, Ireland, 2020, pp. 1–7.
