/*変数宣言*/
DECLARE _start_date,_end_date DATE;

/*初期値セット*/
SET _start_date = '2023-10-01';
SET _end_date = '2024-03-31';

/*-------------------------------------
    集計処理
-------------------------------------*/

WITH
target_mesh AS (
    SELECT
        DISTINCT col_125mesh AS mesh
    FROM
        `prd-analysis.master_v.master_mesh_address_stats`
    WHERE
        pref = '宮城県'
),
poihome as(
    SELECT DISTINCT
        poi.hashed_adid,
        mmas.pref,
        mmas.city
    FROM
        `prd-analysis.master_v.poi_li_monthly` poi
    INNER JOIN
        target_mesh tm
    ON
        safe_cast(tm.mesh as int64) = safe_cast(poi.poi_home_mesh as int64)
    INNER JOIN
        `prd-analysis.master_v.master_mesh_address_stats` mmas
    ON safe_cast(mmas.col_125mesh as int64) = safe_cast(poi.poi_home_mesh as int64)
    WHERE
        poi.date BETWEEN _start_date AND _end_date
),
log as (
    SELECT
        master.hashed_adid,
        poihome.pref,
        poihome.city,
        master.genre_name,
        master.name
    FROM
        `prd-analysis.master_v.personaized` master
    INNER JOIN
        poihome
    ON poihome.hashed_adid = master.hashed_adid
    WHERE
        date(master.sdk_detect_ptime ,'Asia/Tokyo') BETWEEN _start_date AND _end_date
        AND master.name IS NOT NULL
        AND master.is_work = false
        AND mode = "stay"
),
uu as(
    SELECT
        pref,
        city,
        count(hashed_adid) as user_num
    FROM
        log
    GROUP BY
        pref,city
)
SELECT
    log.pref,
    log.city,
    category_master.category,
    category_master.sub_category,
    category_master.genre,
    log.name,
    COUNT(hashed_adid) AS count,
    MIN(user_num) AS num_uu_prefcity
FROM
    log
INNER JOIN
    uu
ON uu.pref = log.pref AND uu.city = log.city
INNER JOIN
    `prd-analysis.pj_persona.personaized_category_flag` category_master
ON category_master.genre = log.genre_name
GROUP BY
    log.pref,
    log.city,
    category_master.category,
    category_master.sub_category,
    category_master.genre,
    log.name