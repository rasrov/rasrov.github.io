window.runCalendarProfile = async function () {
    const wait = ms => new Promise(resolve => setTimeout(resolve, ms));
    const frame = () => new Promise(resolve => requestAnimationFrame(resolve));
    await document.fonts.ready;
    await wait(300);
    const initialAgenda = profileData.agenda.slice();
    const events = [...document.querySelectorAll('.calendar-event')];
    const monthNumber = date => Number(date.slice(0, 4)) * 12 + Number(date.slice(5, 7)) - 1;
    const first = Math.min(...events.map(event => monthNumber(event.dataset.date)));
    const last = Math.max(...events.map(event => monthNumber(event.dataset.date)));
    const samples = [];
    const previous = document.querySelector('#calendar-prev');
    const next = document.querySelector('#calendar-next');
    const click = button => {
        const start = performance.now();
        const mark = profileData.agenda.length;
        button.click();
        return {ms: performance.now() - start, agenda: profileData.agenda.slice(mark)};
    };
    for (let round = 0; round < 3; round++) {
        for (let i = last; i > first; i--) { click(previous); await frame(); }
        for (let i = first; i <= last; i++) {
            // Measure entering the current month from the next month, including the earliest one.
            click(next); await frame();
            samples.push({round, month: i, ...click(previous)});
            await frame();
            if (i < last) { click(next); await frame(); }
        }
    }
    const agendaBeforeScroll = profileData.agenda.length;
    profileData.hero = [];
    for (let i = 0; i <= 100; i++) {
        window.scrollTo({top: (document.documentElement.scrollHeight - innerHeight) * i / 100, behavior: 'instant'});
        await frame();
    }
    await wait(100);
    const summary = values => {
        const sorted = values.slice().sort((a, b) => a - b);
        return {n: sorted.length, median: sorted[Math.floor(sorted.length * 0.5)] ?? 0, p95: sorted[Math.min(sorted.length - 1, Math.floor(sorted.length * 0.95))] ?? 0, max: sorted.at(-1) ?? 0};
    };
    const hero = summary(profileData.hero);
    if (profileData.errors.length) throw new Error(profileData.errors.join('; '));
    return {
        browser: navigator.userAgent, viewport: innerWidth, events: events.length,
        initialAgenda, monthChanges: summary(samples.map(sample => sample.ms)),
        agenda: summary(samples.flatMap(sample => sample.agenda.map(item => item.ms))),
        heroScroll: hero, agendaCallsDuringScroll: profileData.agenda.length - agendaBeforeScroll,
        busiest: samples.filter(sample => sample.agenda.some(item => item.count === Math.max(...samples.flatMap(row => row.agenda.map(item => item.count))))),
        samples
    };
};
