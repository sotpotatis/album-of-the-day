/* dates.js
 * Various utilities related to working with dates.
 * We are already using the magnificent time parsing library Luxon but this helps out with some additional stuff. */
import { DateTime } from 'luxon';
export function getNow() {
	return DateTime.now().setZone('Europe/Stockholm'); // We're working with Swedish timezones!
}
/**
 * Takes a datetime string as input and translates it into a readable string following these rules:
 * - If the date difference between the input is <2 days, you'll get "today" or "yesterday" back.
 * - Otherwise, you will get the date and month back (x june) for example. Note that all returns will be
 * in Swedish!
 * @param date An ISO date string to parse.
 * @param includeYear If set to true, will include the year.
 * @return {string} A human-readable string based on the time delta.
 */
export function dateDifferenceToHumanReadable(date, includeYear = null) {
	const luxonDate = DateTime.fromISO(date);
	const now = getNow();
	const difference = now.diff(luxonDate, ['days', 'years']);
	if (difference.days < 1) {
		// "today"
		return 'idag';
	} else if (difference.days < 2) {
		// "yesterday"
		return 'igår';
	} else {
		return luxonDate
			.setLocale('sv')
			.toFormat(`d MMMM${difference.years > 0 || includeYear ? ' yyyy' : ''}`); // for example, "6 juni" (june 6th). Year may be added.
	}
}
export function getStartAndEndOfMonth(datetime) {
	return [datetime.startOf('month'), datetime.endOf('month')];
}
