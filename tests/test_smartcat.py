import pytest
import requests
from datetime import datetime
from utils import get_difference
from utils import open_db

current_datetime = datetime.now()
shift_breaks = 'shift_breaks'
shift_allowances = 'shift_allowances'
shift_award_interpretation = 'shift_award_interpretation'
shifts = 'shifts'
mydb = None


@pytest.fixture(autouse=True)
def my_setup_and_tear_down():
    etl_enrichment = requests.get('http://localhost:9091/run?ids=1,2,3&user_ids=1,2')
    yield
    global mydb
    mydb = open_db()
    cursor = mydb.cursor()
    cursor.execute("TRUNCATE TABLE {0}".format(shift_breaks))
    cursor.execute("TRUNCATE TABLE {0}".format(shift_allowances))
    cursor.execute("TRUNCATE TABLE {0}".format(shift_award_interpretation))
    cursor.execute("TRUNCATE TABLE {0}".format(shifts))
    cursor.close()
    mydb.close()


@pytest.fixture(autouse=True)
def run_around_tests():
    global mydb
    mydb = open_db();
    yield
    mydb.cursor().close()
    mydb.close()


def test_if_db_is_connected():
    assert mydb.is_connected(), 'Database is not connected.'


def test_if_there_are_any_data_in_db_after_etl():
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM shifts LIMIT 1")
    result = cursor.fetchone()
    assert result is not None, 'There was some problem, database is not filled with expected data'


def test_if_db_has_4_specific_tables():
    cursor = mydb.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM information_schema.tables WHERE table_name IN ('{0}', '{1}', '{2}', '{3}');".format(
            shift_breaks, shift_allowances, shift_award_interpretation, shifts))
    (number_of_rows,) = cursor.fetchone()
    assert number_of_rows == 4


def test_if_etl_enriched_tbl_shift_breaks_with_additional_columns():
    cursor = mydb.cursor()
    cursor.execute("SELECT shift_id, timesheet_id, date FROM {0} LIMIT 1".format(shift_breaks))
    tbl_breaks = cursor.fetchone()
    assert tbl_breaks is not None, 'Table is not enriched with additional column.'


def test_if_etl_enriched_tbl_tbl_shift_allowances_with_additional_columns():
    cursor = mydb.cursor()
    cursor.execute("SELECT shift_id, timesheet_id, date FROM {0} LIMIT 1".format(shift_allowances))
    tbl_allowances = cursor.fetchone()
    assert tbl_allowances is not None, 'Table is not enriched with additional column'


def test_if_etl_enriched_tbl_shift_award_interpretation_with_additional_columns():
    cursor = mydb.cursor()
    cursor.execute("SELECT shift_id, timesheet_id, date FROM {0} LIMIT 1".format(shift_award_interpretation))
    tbl_award_interpretation = cursor.fetchone()
    assert tbl_award_interpretation is not None, 'Table is not enriched with additional column'


def test_if_etl_enriched_tbl_shift_breaks_with_matched_data_from_tbl_shifts():
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM {0} LIMIT 1".format(shift_breaks))
    tbl_breaks = cursor.fetchone()
    cursor.execute("SELECT * FROM {0} WHERE id={1} LIMIT 1".format(shifts, str(tbl_breaks[1])))
    tbl_shift = cursor.fetchone()
    assert tbl_shift is not None, 'Table shifts does not have any data'
    assert tbl_shift[0] == tbl_breaks[1], 'tbl_breaks has invalid data under shift ID column'
    assert tbl_shift[4] == tbl_breaks[3], 'tbl_breaks has invalid data under shift date column'
    assert tbl_shift[1] == tbl_breaks[2], 'tbl_breaks has invalid data under timesheet ID column'


def test_if_etl_enriched_tbl_shift_allowances_with_matched_data_from_tbl_shifts():
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM shift_allowances LIMIT 1")
    tbl_allowances = cursor.fetchone()
    cursor.execute("SELECT * FROM shifts WHERE id=" + str(tbl_allowances[1]) + " LIMIT 1")
    tbl_shift = cursor.fetchone()
    assert tbl_shift is not None, 'Table shifts does not have any data'
    assert tbl_shift[0] == tbl_allowances[1], 'tbl_allowances has invalid data under shift ID column'
    assert tbl_shift[4] == tbl_allowances[3], 'tbl_allowances has invalid data under shift date column'
    assert tbl_shift[1] == tbl_allowances[2], 'tbl_allowances has invalid data under timesheet ID column'


def test_if_etl_enriched_tbl_shift_award_interpretation_with_matched_data_from_tbl_shifts():
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM shift_award_interpretation LIMIT 1")
    tbl_award_interpretation = cursor.fetchone()
    cursor.execute("SELECT * FROM shifts WHERE id=" + str(tbl_award_interpretation[0]) + " LIMIT 1")
    tbl_shift = cursor.fetchone()
    assert tbl_shift is not None, 'Table shifts does not have any data'
    assert tbl_shift[0] == tbl_award_interpretation[
        0], 'tbl_award_interpretation has invalid data under shift ID column '
    assert tbl_shift[4] == tbl_award_interpretation[
        3], 'tbl_award_interpretation has invalid data under shift date column'
    assert tbl_shift[1] == tbl_award_interpretation[
        1], 'tbl_award_interpretation has invalid data under timesheet ID column'


def test_if_etl_converted_timestamps_to_est_timezone_in_tbl_shift_allowances():
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM shift_allowances LIMIT 1")
    tbl_shift_allowances = cursor.fetchone()
    timezone_delta = get_difference(current_datetime, tbl_shift_allowances[8])
    assert timezone_delta == 7 or timezone_delta == 6, 'timestamps are not converted to the EST timezone'


def test_if_etl_converted_timestamps_to_est_timezone_in_tbl_shift_breaks():
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM shift_breaks LIMIT 1")
    tbl_shift_breaks = cursor.fetchone()
    timezone_delta = get_difference(current_datetime, tbl_shift_breaks[9])
    assert timezone_delta == 7 or timezone_delta == 6, 'timestamps are not converted to the EST timezone'


def test_if_etl_converted_timestamps_to_est_timezone_in_tbl_shift_award_interpretation():
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM shift_award_interpretation LIMIT 1")
    tbl_shift_award_interpretation = cursor.fetchone()
    timezone_delta = get_difference(current_datetime, tbl_shift_award_interpretation[10])
    assert timezone_delta == 7 or timezone_delta == 6, 'timestamps are not converted to the EST timezone'