<!-- About page
A page showing some information about this website. -->
<script>
	import Page from '../../components/Page.svelte';
	import HeaderTitle from '../../components/Header/HeaderTitle.svelte';
	import HeadingDivider from '../../components/Generic/HeadingDivider.svelte';
</script>

<Page>
	<svelte:fragment slot="header">
		<HeaderTitle title="om hemsidan" description="ett album om dagen - och mer än så." />
	</svelte:fragment>
	<svelte:fragment slot="page">
		<div class="text-left md:w-3/4 lg:w-1/2">
			<HeadingDivider title="Vem ligger bakom denna sida?" />
			<p>
				hej! mitt namn är Albin. sedan juni 2022 har jag drivit en story på Snapchat där jag skrivit
				om ett album, varje dag. storyn är fortfarande aktiv och har cirka 10 medlemmar. jag ville
				själv ha någonstans att samla det jag skrivit om samtidigt som jag känner att det jag
				skriver är värda att vara tillgängliga för en större publik och längre än 24 timmar.
			</p>
			<HeadingDivider title="Album of the day" />
			<p>
				konceptet bakom album of the day är enkelt - jag skriver om ett nytt album, varje dag. en
				bra funktion med denna sida är att jag kan dubbelkolla att jag inte skrivit om något album
				tidigare, för att minska risken för dubletter. förutom vissa speciella temaveckor (t.ex. "en
				återblick på 2022") så är tanken att varje idag ska innehålla ett nytt, unikt album.
			</p>
			<p>
				Du kan hitta alla album of the day sorterat på månad <a href="/album-of-the-days">här!</a>
			</p>
			<HeadingDivider title="Listor" />
			<p>
				en funktion på denna hemsida är listor. i listor samlar jag album i olika konstellationer.
				kika in på alla listor <a href="/lists">här</a>!
			</p>
			<HeadingDivider title="Dagliga rotationer" />
			<p>
				för att se vad jag lyssnat på över tid finns mina "Dagliga rotationer". här kan du dag för
				dag följa vad jag har lyssnat på för album och för genrer. du hittar alla dagliga rotationer
				sorterat på månad <a href="/daily-rotations">här</a>.
			</p>
			<HeadingDivider title="Spara till Spotify" />
			<p>
				på sidan kan du även spara de flesta album till din Spotify-profil, så att du kan lyssna på
				de senare. detta görs genom att klicka på knappen "Lägg till på Spotify" vid respektive
				album. gå till ditt Spotify-bibliotek, så kommer du att hitta en spellista med namnet "Album
				of the day: sparat". där finns alla sparade album!
			</p>
			<HeadingDivider title="Licenser" />
			<p>
				innehåll som <i>jag</i> skrivit, det vill säga kommentarer om album och komponering av
				listor är licenserade under
				<a href="https://creativecommons.org/licenses/by-nc/4.0/" target="_blank">CC-BY-NC 4.0</a>.
				observera däremot att albumomslag och annan metadata, till exempel albumomslag och
				genrebeskrivningar, tillhör <a href="https://spotify.com/" target="_blank">Spotify</a>
				(albumomslag) och <a href="https://last.fm/" target="_blank">Last.FM</a> (genrebeskrivningar).
				dessa omfattas av andra licenser.
			</p>
			<HeadingDivider title="Kontakt" />
			<p>du kan mejla mig på <a href="mailto:albin@albins.website">albin@albins.website</a>.</p>
			<HeadingDivider title="Open source" />
			<p>
				sidans kompletta källkod finns tillgänglig på <a
					href="https://github.com/sotpotatis/album-of-the-day"
					target="_blank">GitHub</a
				>.
			</p>
		</div>
	</svelte:fragment>
</Page>
