#!
# -*- coding: utf-8 -*-
"""
Created on 2022-07-16
@author: Edmund Bennett
@email: bennettedmund@gmail.com
"""

import re
from typing import Optional, List
from datetime import datetime

from bfsa.utils.logger import logger as log


class DatetimeParser:

    __file_contents_pre__ = "([a-zA-Z\\s\\-_.0-9]+?)"
    __file_contents_post__ = "([a-zA-Z\\s\\-_.0-9]+)?"

    __sep__ = "([-\\.\\/\\\\s:]?)"
    __day__ = "(0?[1-9](?![0-9]{1,})|[1-2][0-9](?![0-9]{1,})|3[0-1](?![0-9]+))"
    __month__ = "(0[1-9]|1[0-2]|January|Jan|February|Feb|March|Mar|April|Apr|May|June|Jun|July|Jul|August|Aug|September|Sep|October|Oct|November|Nov|December|Dec|[1-9])"  # MATCHES: 1, 03, 10, 11, 12, Jan, December; DOES NOT MATCH: 001, 011, Janu
    __year__ = "([0-3]?[0-9]{1,3}|[0-9]{2})"
    __t_space__ = "([tT\\s]?)"
    __hour__ = "([0-1][0-9]|2[0-4]|[0-9])?"
    __min__ = "([0-5][0-9])?"
    __sec__ = "([0-5][0-9])?"
    __p__ = "(\\.)?"
    __micro__ = "([0-9]{0,6})?"
    __zone__ = "(Z|UTC)?"
    __pm__ = "(\\+|-)?"
    __h1__ = "([0-1][0-9]|2[0-4])?"
    __h2__ = "(:?[0-1][0-9]|2[0-4])?"
    __space__ = "(\\s)?"

    __f_year_long__ = "%Y"
    __f_year_short__ = "%y"
    __f_month_text_long__ = "%B"
    __f_month_text_short__ = "%b"
    __f_month_num__ = "%m"
    __f_day__ = "%d"
    __f_hour__ = "%H"
    __f_min__ = "%M"
    __f_sec__ = "%S"
    __f_weekday_name__ = "%A"
    __f_day_of_week__ = "%w"  # 0 is Sunday, 6 is Saturday
    __f_twelve_hour__ = "%I"
    __f_am_pm__ = "%p"
    __f_micro__ = "%f"
    __f_time_zone_offset__ = "%z"
    __f_time_zone_name__ = "%Z"
    __f_day_of_year__ = "%j"
    __f_zero_padded_week_no__ = "%U"
    __f_week_no__ = "%W"
    __f_locale_datetime_rep__ = "%c"
    __f_locale_date_rep__ = "%x"
    __f_locale_time_rep__ = "%X"
    __f_percentage_symbol__ = "%%"

    common_validation_capture_list = [
        __t_space__,
        __hour__,
        __sep__,
        __min__,
        __sep__,
        __sec__,
        __p__,
        __micro__,
        __space__,
        __zone__,
        __pm__,
        __h1__,
        __h2__,
    ]

    full_validation_capture_list_ymd = [
        __year__,
        __sep__,
        __month__,
        __sep__,
        __day__,
    ] + common_validation_capture_list
    full_validation_capture_list_dmy = [
        __day__,
        __sep__,
        __month__,
        __sep__,
        __year__,
    ] + common_validation_capture_list
    full_validation_capture_list_mdy = [
        __month__,
        __sep__,
        __day__,
        __sep__,
        __year__,
    ] + common_validation_capture_list

    exclusion_list = [__sep__]
    removal_list = [
        __file_contents_pre__,
        __file_contents_post__,
    ]

    @staticmethod
    def identify_datetimes(
        input_str_list: List[str],
        month_day_year_hint=False,
        day_month_year_hint=False,
        year_month_day_hint=False,
    ) -> List[datetime]:
        """Returns a datetime representation of a list of strings representing datetime values"""
        assert (
            month_day_year_hint + day_month_year_hint + year_month_day_hint <= 1
        ), "Multiple conflicting date format hints provided"

        log.debug("Starting pre-processing")
        parsed_input_str_list = []
        parsed_datetime_year_month_day_list = []
        parsed_datetime_month_day_year_list = []
        parsed_datetime_day_month_year_list = []
        parsed_datetime_year_month_day_conversion_ok = True
        parsed_datetime_month_day_year_conversion_ok = True
        parsed_datetime_day_month_year_conversion_ok = True
        for input_str in input_str_list:
            parsed_input_str = DatetimeParser.__preprocess_input_str__(input_str)
            parsed_input_str_list.append(parsed_input_str)

            parsed_datetime_year_month_day = DatetimeParser.__apply_regex__(
                DatetimeParser.full_validation_capture_list_ymd, parsed_input_str
            )
            parsed_datetime_year_month_day_list.append(parsed_datetime_year_month_day)
            parsed_datetime_year_month_day_conversion_ok = (
                False
                if not parsed_datetime_year_month_day_conversion_ok
                or parsed_datetime_year_month_day is None
                else True
            )

            parsed_datetime_month_day_year = DatetimeParser.__apply_regex__(
                DatetimeParser.full_validation_capture_list_mdy, parsed_input_str
            )
            parsed_datetime_month_day_year_list.append(parsed_datetime_month_day_year)
            parsed_datetime_month_day_year_conversion_ok = (
                False
                if not parsed_datetime_month_day_year_conversion_ok
                or parsed_datetime_month_day_year is None
                else True
            )

            parsed_datetime_day_month_year = DatetimeParser.__apply_regex__(
                DatetimeParser.full_validation_capture_list_dmy, parsed_input_str
            )
            parsed_datetime_day_month_year_list.append(parsed_datetime_day_month_year)
            parsed_datetime_day_month_year_conversion_ok = (
                False
                if not parsed_datetime_day_month_year_conversion_ok
                or parsed_datetime_day_month_year is None
                else True
            )

        log.debug("Constructing and applying regex")
        now = datetime.now()
        if (
            not parsed_datetime_year_month_day_conversion_ok
            and not parsed_datetime_month_day_year_conversion_ok
            and not parsed_datetime_day_month_year_conversion_ok
        ):
            log.debug(
                "No single regex applicable to all datetime values - fall back to flexible mode"
            )
            converted_str_list = []
            for parsed_input_str in parsed_input_str_list:
                converted_str = DatetimeParser.identify_datetime(parsed_input_str)
                converted_str_list.append(converted_str)
            return converted_str_list
        elif (
            parsed_datetime_year_month_day_conversion_ok
            and not parsed_datetime_month_day_year_conversion_ok
            and not parsed_datetime_day_month_year_conversion_ok
        ):
            log.debug(
                "Only year-month-day regex applicable to all datetime values - using that"
            )
            return parsed_datetime_year_month_day_list
        elif (
            not parsed_datetime_year_month_day_conversion_ok
            and parsed_datetime_month_day_year_conversion_ok
            and not parsed_datetime_day_month_year_conversion_ok
        ):
            log.debug(
                "Only month-day-year regex applicable to all datetime values - using that"
            )
            return parsed_datetime_month_day_year_list
        elif (
            not parsed_datetime_year_month_day_conversion_ok
            and not parsed_datetime_month_day_year_conversion_ok
            and parsed_datetime_day_month_year_conversion_ok
        ):
            log.debug(
                "Only day-month-year regex applicable to all datetime values - using that"
            )
            return parsed_datetime_day_month_year_list
        elif (
            parsed_datetime_year_month_day_conversion_ok
            and parsed_datetime_month_day_year_conversion_ok
            and not parsed_datetime_day_month_year_conversion_ok
        ):
            log.debug(
                "Both year-month-day and month-day-year regexes applicable to all datetime values"
            )
            if year_month_day_hint:
                return parsed_datetime_year_month_day_list
            if month_day_year_hint:
                return parsed_datetime_month_day_year_list
            ymd_offset = sum(
                [
                    abs(now - x).total_seconds()
                    for x in parsed_datetime_year_month_day_list
                ]
            )
            mdy_offset = sum(
                [
                    abs(now - x).total_seconds()
                    for x in parsed_datetime_month_day_year_list
                ]
            )
            return (
                parsed_datetime_year_month_day_list
                if ymd_offset < mdy_offset
                else parsed_datetime_month_day_year_list
            )
        elif (
            parsed_datetime_year_month_day_conversion_ok
            and not parsed_datetime_month_day_year_conversion_ok
            and parsed_datetime_day_month_year_conversion_ok
        ):
            log.debug(
                "Both year-month-day and day-month-year regexes applicable to all datetime values"
            )
            if year_month_day_hint:
                return parsed_datetime_year_month_day_list
            if day_month_year_hint:
                return parsed_datetime_day_month_year_list
            ymd_offset = sum(
                [
                    abs(now - x).total_seconds()
                    for x in parsed_datetime_year_month_day_list
                ]
            )
            dmy_offset = sum(
                [
                    abs(now - x).total_seconds()
                    for x in parsed_datetime_day_month_year_list
                ]
            )
            return (
                parsed_datetime_year_month_day_list
                if ymd_offset < dmy_offset
                else parsed_datetime_day_month_year_list
            )
        elif (
            not parsed_datetime_year_month_day_conversion_ok
            and parsed_datetime_month_day_year_conversion_ok
            and parsed_datetime_day_month_year_conversion_ok
        ):
            log.debug(
                "Both month-day-year and day-month-year regexes applicable to all datetime values"
            )
            if month_day_year_hint:
                return parsed_datetime_month_day_year_list
            if day_month_year_hint:
                return parsed_datetime_day_month_year_list
            mdy_offset = sum(
                [
                    abs(now - x).total_seconds()
                    for x in parsed_datetime_month_day_year_list
                ]
            )
            dmy_offset = sum(
                [
                    abs(now - x).total_seconds()
                    for x in parsed_datetime_day_month_year_list
                ]
            )
            return (
                parsed_datetime_month_day_year_list
                if mdy_offset < dmy_offset
                else parsed_datetime_day_month_year_list
            )
        elif (
            parsed_datetime_year_month_day_conversion_ok
            and parsed_datetime_month_day_year_conversion_ok
            and parsed_datetime_day_month_year_conversion_ok
        ):
            log.debug(
                "All of year-month-day, month-day-year and day-month-year regexes applicable to all datetime values"
            )
            if year_month_day_hint:
                return parsed_datetime_year_month_day_list
            if month_day_year_hint:
                return parsed_datetime_month_day_year_list
            if day_month_year_hint:
                return parsed_datetime_day_month_year_list
            ymd_offset = sum(
                [
                    abs(now - x).total_seconds()
                    for x in parsed_datetime_year_month_day_list
                ]
            )
            mdy_offset = sum(
                [
                    abs(now - x).total_seconds()
                    for x in parsed_datetime_month_day_year_list
                ]
            )
            dmy_offset = sum(
                [
                    abs(now - x).total_seconds()
                    for x in parsed_datetime_day_month_year_list
                ]
            )
            first_stage_dates, first_stage_dates_offset = (
                (parsed_datetime_year_month_day_list, ymd_offset)
                if ymd_offset < mdy_offset
                else (parsed_datetime_month_day_year_list, mdy_offset)
            )
            return (
                first_stage_dates
                if first_stage_dates_offset < dmy_offset
                else parsed_datetime_day_month_year_list
            )

    @staticmethod
    def identify_datetime(
        input_str: str = None,
        month_day_year_hint=False,
        day_month_year_hint=False,
        year_month_day_hint=False,
    ) -> Optional[datetime]:
        """Returns a datetime representation of the input argument if it is a valid datetime, else None"""

        if input_str is None:
            log.debug("Putative datetime string is: None")
            return None

        assert (
            month_day_year_hint + day_month_year_hint + year_month_day_hint <= 1
        ), "Multiple conflicting date format hints provided"

        parsed_input_str = DatetimeParser.__preprocess_input_str__(input_str)

        parsed_datetime_year_month_day = DatetimeParser.__apply_regex__(
            DatetimeParser.full_validation_capture_list_ymd, parsed_input_str
        )
        parsed_datetime_month_day_year = DatetimeParser.__apply_regex__(
            DatetimeParser.full_validation_capture_list_mdy, parsed_input_str
        )
        parsed_datetime_day_month_year = DatetimeParser.__apply_regex__(
            DatetimeParser.full_validation_capture_list_dmy, parsed_input_str
        )

        return DatetimeParser.__combine_date_format_logic__(
            parsed_datetime_year_month_day,
            parsed_datetime_month_day_year,
            parsed_datetime_day_month_year,
            month_day_year_hint,
            day_month_year_hint,
            year_month_day_hint,
        )

    @staticmethod
    def extract_datetime(
        input_str: str = None,
        month_day_year_hint=False,
        day_month_year_hint=False,
        year_month_day_hint=False,
    ) -> Optional[datetime]:
        """Returns a datetime representation of the input argument if it contains a valid datetime, else None"""
        if input_str is None:
            log.debug("Putative datetime string is: None")
            return None

        assert (
            month_day_year_hint + day_month_year_hint + year_month_day_hint <= 1
        ), "Multiple conflicting date format hints provided"

        parsed_input_str = DatetimeParser.__preprocess_input_str__(input_str)

        parsed_datetime_year_month_day = DatetimeParser.__apply_regex__(
            DatetimeParser.__extraction_wrapper__(
                DatetimeParser.full_validation_capture_list_ymd
            ),
            parsed_input_str,
        )

        parsed_datetime_month_day_year = DatetimeParser.__apply_regex__(
            DatetimeParser.__extraction_wrapper__(
                DatetimeParser.full_validation_capture_list_mdy
            ),
            parsed_input_str,
        )

        parsed_datetime_day_month_year = DatetimeParser.__apply_regex__(
            DatetimeParser.__extraction_wrapper__(
                DatetimeParser.full_validation_capture_list_dmy
            ),
            parsed_input_str,
        )

        return DatetimeParser.__combine_date_format_logic__(
            parsed_datetime_year_month_day,
            parsed_datetime_month_day_year,
            parsed_datetime_day_month_year,
            month_day_year_hint,
            day_month_year_hint,
            year_month_day_hint,
        )

    @staticmethod
    def __extraction_wrapper__(capture_list):
        return (
            [DatetimeParser.__file_contents_pre__]
            + capture_list
            + [DatetimeParser.__file_contents_post__]
        )

    @staticmethod
    def __preprocess_input_str__(input_str) -> str:
        """Preprocessor for parsing engine"""
        input_str = input_str.strip()
        return input_str

    @staticmethod
    def __combine_date_format_logic__(
        parsed_datetime_year_month_day,
        parsed_datetime_month_day_year,
        parsed_datetime_day_month_year,
        month_day_year_hint,
        day_month_year_hint,
        year_month_day_hint,
    ):
        log.debug(
            f"Combining output datetime formats\n"
            f"Year month day: {parsed_datetime_year_month_day}\n "
            f"Year month day: {parsed_datetime_year_month_day}\n "
            f"Year month day: {parsed_datetime_year_month_day}\n"
        )
        now = datetime.now()
        if (
            parsed_datetime_year_month_day is None
            and parsed_datetime_month_day_year is None
            and parsed_datetime_day_month_year is None
        ):
            log.debug("All returned datetime values are None. Returning: None")
            return None
        elif (
            parsed_datetime_year_month_day is not None
            and parsed_datetime_month_day_year is None
            and parsed_datetime_day_month_year is None
        ):
            log.debug(
                f"Only year-month-day format is not None. Returning: {parsed_datetime_year_month_day}"
            )
            return parsed_datetime_year_month_day
        elif (
            parsed_datetime_year_month_day is None
            and parsed_datetime_month_day_year is not None
            and parsed_datetime_day_month_year is None
        ):
            log.debug(
                f"Only month-day-year format is not None. Returning: {parsed_datetime_month_day_year}"
            )
            return parsed_datetime_month_day_year
        elif (
            parsed_datetime_year_month_day is None
            and parsed_datetime_month_day_year is None
            and parsed_datetime_day_month_year is not None
        ):
            log.debug(
                f"Only day-month-year format is not None. Returning: {parsed_datetime_day_month_year}"
            )
            return parsed_datetime_day_month_year
        elif (
            parsed_datetime_year_month_day is None
            and parsed_datetime_month_day_year is not None
            and parsed_datetime_day_month_year is not None
        ):
            log.debug(f"Both day-month-year and month-day-year formats are not None.")
            if month_day_year_hint:
                return parsed_datetime_month_day_year
            if day_month_year_hint:
                return parsed_datetime_month_day_year
            dmy_offset = abs(parsed_datetime_day_month_year - now)
            mdy_offset = abs(parsed_datetime_month_day_year - now)
            return (
                parsed_datetime_day_month_year
                if dmy_offset < mdy_offset
                else parsed_datetime_month_day_year
            )
        elif (
            parsed_datetime_year_month_day is not None
            and parsed_datetime_month_day_year is None
            and parsed_datetime_day_month_year is not None
        ):
            log.debug(f"Both year-month-day and day-month-year formats are not None.")
            if year_month_day_hint:
                return parsed_datetime_year_month_day
            if day_month_year_hint:
                return parsed_datetime_day_month_year
            ymd_offset = abs(parsed_datetime_year_month_day - now)
            dmy_offset = abs(parsed_datetime_day_month_year - now)
            return (
                parsed_datetime_year_month_day
                if ymd_offset < dmy_offset
                else parsed_datetime_day_month_year
            )
        elif (
            parsed_datetime_year_month_day is not None
            and parsed_datetime_month_day_year is not None
            and parsed_datetime_day_month_year is None
        ):
            log.debug(f"Both year-month-day and month-day-year formats are not None.")
            if year_month_day_hint:
                return parsed_datetime_year_month_day
            if month_day_year_hint:
                return parsed_datetime_month_day_year
            ymd_offset = abs(parsed_datetime_year_month_day - now)
            mdy_offset = abs(parsed_datetime_month_day_year - now)
            return (
                parsed_datetime_year_month_day
                if ymd_offset < mdy_offset
                else parsed_datetime_month_day_year
            )
        elif (
            parsed_datetime_year_month_day is not None
            and parsed_datetime_month_day_year is not None
            and parsed_datetime_day_month_year is not None
        ):
            log.debug(
                f"Each of year-month-day, day-month-year and month-day-year formats are not None."
            )
            if year_month_day_hint:
                return parsed_datetime_year_month_day
            if month_day_year_hint:
                return parsed_datetime_month_day_year
            if day_month_year_hint:
                return parsed_datetime_day_month_year
            ymd_offset = abs(parsed_datetime_year_month_day - now)
            mdy_offset = abs(parsed_datetime_month_day_year - now)
            dmy_offset = abs(parsed_datetime_day_month_year - now)
            first_stage_date = (
                parsed_datetime_month_day_year
                if mdy_offset < dmy_offset
                else parsed_datetime_day_month_year
            )
            first_stage_date_offset = abs(first_stage_date - now)
            return (
                parsed_datetime_year_month_day
                if ymd_offset < first_stage_date_offset
                else first_stage_date
            )

    @staticmethod
    def __apply_regex__(regex_component_list, search_str):
        match = re.search(
            DatetimeParser.__build_regex__(regex_component_list),
            search_str,
        )
        if match is None:
            log.debug(f"No regex match on putative datetime string: {search_str}")
            return None
        else:
            log.debug(f"Match on putative datetime string: {search_str}")
            fmt = search_str
            for t, m in zip(
                regex_component_list,
                match.groups(),
            ):

                if m is not None and m and t not in DatetimeParser.exclusion_list:
                    log.debug(f"Capture group: {t} match element: {m}")
                    if t not in DatetimeParser.removal_list:
                        format_component = DatetimeParser.__capture_group_mapping__(
                            t, m, fmt
                        )
                        if format_component is not None:
                            log.debug(
                                f"Converting existing format: {fmt} using new format component: {format_component} matched to: {m}"
                            )
                            fmt = fmt.replace(m, format_component, 1)
                    else:  # remove
                        fmt = fmt.replace(m, "", 1)
                        search_str = search_str.replace(m, "", 1)

        # special cases: strip out final characters in the set
        if search_str[-1] == fmt[-1] and search_str[-1] in {"."}:
            fmt = fmt[0:-1]
            search_str = search_str[0:-1]

        try:
            parsed_datetime = datetime.strptime(search_str, fmt)
            log.debug(
                f"Completed parsing of putative datetime: {search_str} with output: {parsed_datetime}"
            )
            return parsed_datetime
        except NameError as e:
            log.warning(
                f"Conversion failure for putative datetime string: {search_str} with conversion format: {fmt} and exception: {e}"
            )
            return None

    @staticmethod
    def __build_regex__(capture_list):
        validation_regex = "^"
        for capture_group in capture_list:
            validation_regex += capture_group
        validation_regex += "$"
        return validation_regex

    @staticmethod
    def __yearly_data_parser__(value):
        if len(value) == 4:
            log.debug(f"Value: {value} parsed as long year number.")
            return DatetimeParser.__f_year_long__
        elif len(value) == 2:
            log.debug(f"Value: {value} parsed as short year number.")
            return DatetimeParser.__f_year_short__

    @staticmethod
    def __monthly_data_parser__(value):
        if value in [
            "01",
            "02",
            "03",
            "04",
            "05",
            "06",
            "07",
            "08",
            "09",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "11",
            "12",
        ]:
            log.debug(f"Value: {value} parsed as month number.")
            return DatetimeParser.__f_month_num__
        elif value.lower() in [
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "december",
        ]:  # month full name
            log.debug(f"Value: {value} parsed as full month name.")
            return DatetimeParser.__f_month_text_long__
        elif value.lower() in [
            "jan",
            "feb",
            "mar",
            "apr",
            "may",
            "jun",
            "jul",
            "aug",
            "sep",
            "oct",
            "nov",
            "dec",
        ]:  # month abbreviated name
            log.debug(f"Value: {value} parsed as short month name.")
            return DatetimeParser.__f_month_text_short__
        else:
            log.debug(f"Value: {value} not parsed.")
            return None

    @staticmethod
    def __capture_group_mapping__(capture_group, value, current_format):

        years_taken = DatetimeParser.__f_year_short__ in current_format.lower()
        months_taken = (
            DatetimeParser.__f_month_num__ in current_format
            or DatetimeParser.__f_month_text_short__ in current_format.lower()
        )
        days_taken = DatetimeParser.__f_day__ in current_format
        hours_taken = DatetimeParser.__f_hour__ in current_format
        mins_taken = DatetimeParser.__f_min__ in current_format
        seconds_taken = DatetimeParser.__f_sec__ in current_format

        if capture_group == DatetimeParser.__year__ and not years_taken:
            log.debug(
                f"Capture group: {capture_group} accessed processing value: {value}"
            )
            if (
                years_taken
                and months_taken
                and days_taken
                and hours_taken
                and mins_taken
                and seconds_taken
            ):
                log.debug(
                    f"Value: {value} obtained via capture group: {capture_group} cannot be parsed"
                )
                return None
            if "%" not in current_format:  # no formatting so far
                return DatetimeParser.__yearly_data_parser__(value)
            if (
                years_taken
            ):  # assuming YY(YY) -> mm/b/B -> DD -> HH -> MM -> SS ordering
                if not months_taken:
                    return DatetimeParser.__monthly_data_parser__(value)
                if not days_taken:
                    return DatetimeParser.__f_day__
            if days_taken:
                if (
                    not months_taken
                ):  # assuming DD -> mm/b/B -> YY(YY) -> HH -> MM -> SS ordering
                    return DatetimeParser.__monthly_data_parser__(value)
                if not years_taken:
                    if len(value) == 2:
                        return DatetimeParser.__f_year_short__
                    else:
                        return DatetimeParser.__f_year_long__
            if not hours_taken:
                return DatetimeParser.__f_hour__
            if not mins_taken:
                return DatetimeParser.__f_min__
            if not seconds_taken:
                return DatetimeParser.__f_sec__
        elif capture_group == DatetimeParser.__month__ and not months_taken:
            log.debug(
                f"Capture group: {capture_group} accessed processing value: {value}"
            )
            if (
                years_taken
                and months_taken
                and days_taken
                and hours_taken
                and mins_taken
                and seconds_taken
            ):
                log.debug(
                    f"Value: {value} obtained via capture group: {capture_group} cannot be parsed"
                )
                return None
            if (
                "%" not in current_format
            ):  # no formatting so far (get provisional formatting and adjust depending on year position)
                month_format = DatetimeParser.__monthly_data_parser__(value)
                return month_format
            if (
                years_taken
            ):  # assuming YY(YY) -> mm/b/B -> DD -> HH -> MM -> SS ordering
                if not months_taken:
                    return DatetimeParser.__monthly_data_parser__(value)
            if (
                days_taken
            ):  # assuming DD -> mm/b/B <- OR -> YY(YY) -> HH -> MM -> SS ordering
                if not months_taken:
                    return DatetimeParser.__monthly_data_parser__(value)
            if not hours_taken:
                return DatetimeParser.__f_hour__
            if not mins_taken:
                return DatetimeParser.__f_min__
            if not seconds_taken:
                return DatetimeParser.__f_sec__
        elif capture_group == DatetimeParser.__day__ and not days_taken:
            log.debug(
                f"Capture group: {capture_group} accessed processing value: {value}"
            )
            if not days_taken:
                return DatetimeParser.__f_day__
        elif capture_group == DatetimeParser.__t_space__:
            log.debug(
                f"Capture group: {capture_group} accessed processing value: {value}"
            )
            return value
        elif capture_group == DatetimeParser.__hour__ and not hours_taken:
            log.debug(
                f"Capture group: {capture_group} accessed processing value: {value}"
            )
            return DatetimeParser.__f_hour__
        elif capture_group == DatetimeParser.__min__ and not mins_taken:
            log.debug(
                f"Capture group: {capture_group} accessed processing value: {value}"
            )
            return DatetimeParser.__f_min__
        elif capture_group == DatetimeParser.__sec__ and not seconds_taken:
            log.debug(
                f"Capture group: {capture_group} accessed processing value: {value}"
            )
            return DatetimeParser.__f_sec__
        elif capture_group == DatetimeParser.__p__:
            log.debug(
                f"Capture group: {capture_group} accessed processing value: {value}"
            )
            return value
        elif capture_group == DatetimeParser.__micro__:
            log.debug(
                f"Capture group: {capture_group} accessed processing value: {value}"
            )
            return DatetimeParser.__f_micro__
        elif capture_group == DatetimeParser.__space__:
            log.debug(
                f"Capture group: {capture_group} accessed processing value: {value}"
            )
            return value
        elif capture_group == DatetimeParser.__zone__:
            log.debug(
                f"Capture group: {capture_group} accessed processing value: {value}"
            )
            return value
        elif capture_group == DatetimeParser.__pm__:
            log.debug(
                f"Capture group: {capture_group} accessed processing value: {value}"
            )
            return value
        elif capture_group == DatetimeParser.__h1__:
            log.debug(
                f"Capture group: {capture_group} accessed processing value: {value}"
            )
            return value
        elif capture_group == DatetimeParser.__h2__:
            log.debug(
                f"Capture group: {capture_group} accessed processing value: {value}"
            )
            return value


if __name__ == "__main__":
    pass
