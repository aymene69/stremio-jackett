document.addEventListener('DOMContentLoaded', function () {
    updateProviderFields();
});

function setElementDisplay(elementId, displayStatus) {
    const element = document.getElementById(elementId);
    if (!element) {
        return;
    }
    element.style.display = displayStatus;
}

function getValue(elementId) {
    return document.getElementById(elementId).value;
}

function updateProviderFields(isChangeEvent = false) {
    if (document.getElementById('debrid').checked) {
        setElementDisplay('debrid-fields', 'block');
    } else {
        setElementDisplay('debrid-fields', 'none');
    }
    if (document.getElementById('jackett')?.checked) {
        setElementDisplay('jackett-fields', 'block');
    } else {
        setElementDisplay('jackett-fields', 'none');
    }
    if (!isChangeEvent) {
        if (document.getElementById('jackett-fields')) {
            document.getElementById('jackett-host').value = '';
            document.getElementById('jackett-api').value = '';
        }
        document.getElementById('debrid-api').value = '';
    }
}

function loadData() {
    var currentUrl = window.location.href;
    var data = currentUrl.match(/\/([^\/]+)\/configure$/);
    if (data) {
        data = atob(data[1]);
        data = JSON.parse(data);
        if (document.getElementById('jackett-fields')) {
            document.getElementById('jackett-host').value = data.jackettHost;
            document.getElementById('jackett-api').value = data.jackettApiKey;
        }
        document.getElementById('debrid-api').value = data.debridKey;
        document.getElementById('tmdb-api').value = data.tmdbApi;
        document.getElementById('service').value = data.service;
        document.getElementById('exclusion-keywords').value = (data.exclusionKeywords || []).join(', ');
        document.getElementById('maxSize').value = data.maxSize;
        document.getElementById('resultsPerQuality').value = data.resultsPerQuality;
        document.getElementById('maxResults').value = data.maxResults;
        if (document.getElementById('jackett')) {
            document.getElementById('jackett').checked = data.jackett;
        }
        if (document.getElementById('cache')) {
            document.getElementById('cache').checked = data.cache;
        }
        document.getElementById('torrenting').checked = data.torrenting;
        document.getElementById('debrid').checked = data.debrid;
        if (data.sort === 'quality') {
            document.getElementById('quality').checked = true;
        }
        if (data.sort === 'sizedesc') {
            document.getElementById('sizedesc').checked = true;
        }
        if (data.sort === 'sizeasc') {
            document.getElementById('sizeasc').checked = true;
        }
        if (data.sort === 'qualitythensize') {
            document.getElementById('qualitythensize').checked = true;
        }
        if (data.exclusion.includes('4k')) {
            document.getElementById('4k').checked = true;
        }
        if (data.exclusion.includes('1080p')) {
            document.getElementById('1080p').checked = true;
        }
        if (data.exclusion.includes('720p')) {
            document.getElementById('720p').checked = true;
        }
        if (data.exclusion.includes('480p')) {
            document.getElementById('480p').checked = true;
        }
        if (data.exclusion.includes('rips')) {
            document.getElementById('rips').checked = true;
        }
        if (data.exclusion.includes('cam')) {
            document.getElementById('cam').checked = true;
        }
        if (data.languages.includes('en')) {
            document.getElementById('en').checked = true;
        }
        if (data.languages.includes('fr')) {
            document.getElementById('fr').checked = true;
        }
        if (data.languages.includes('es')) {
            document.getElementById('es').checked = true;
        }
        if (data.languages.includes('de')) {
            document.getElementById('de').checked = true;
        }
        if (data.languages.includes('it')) {
            document.getElementById('it').checked = true;
        }
        if (data.languages.includes('pt')) {
            document.getElementById('pt').checked = true;
        }
        if (data.languages.includes('ru')) {
            document.getElementById('ru').checked = true;
        }
        if (data.languages.includes('in')) {
            document.getElementById('in').checked = true;
        }
        if (data.languages.includes('nl')) {
            document.getElementById('nl').checked = true;
        }
        if (data.languages.includes('hu')) {
            document.getElementById('hu').checked = true;
        }
        if (data.languages.includes('la')) {
            document.getElementById('la').checked = true;
        }
        if (data.languages.includes('multi')) {
            document.getElementById('multi').checked = true;
        }

    }
}

let showLanguageCheckBoxes = true;

function showCheckboxes() {
    let checkboxes = document.getElementById("languageCheckBoxes");

    if (showLanguageCheckBoxes) {
        checkboxes.style.display = "block";
        showLanguageCheckBoxes = false;
    } else {
        checkboxes.style.display = "none";
        showLanguageCheckBoxes = true;
    }
}

loadData();

function getLink(method) {
    const addonHost = new URL(window.location.href).protocol.replace(':', '') + "://" + new URL(window.location.href).host
    const jackettHost = document.getElementById('jackett-host')?.value;
    const jackettApi = document.getElementById('jackett-api')?.value;
    const debridApi = document.getElementById('debrid-api').value;
    const tmdbApi = document.getElementById('tmdb-api').value;
    const service = document.getElementById('service').value;
    const exclusionKeywords = document.getElementById('exclusion-keywords').value.split(',').map(keyword => keyword.trim()).filter(keyword => keyword !== '');
    let maxSize = document.getElementById('maxSize').value;
    let resultsPerQuality = document.getElementById('resultsPerQuality').value;
    let maxResults = document.getElementById('maxResults').value;
    const jackett = document.getElementById('jackett')?.checked;
    const cache = document.getElementById('cache')?.checked;
    const torrenting = document.getElementById('torrenting').checked;
    const debrid = document.getElementById('debrid').checked;
    const qualityExclusion = [];
    if (document.getElementById('4k').checked) {
        qualityExclusion.push('4k');
    }
    if (document.getElementById('1080p').checked) {
        qualityExclusion.push('1080p');
    }
    if (document.getElementById('720p').checked) {
        qualityExclusion.push('720p');
    }
    if (document.getElementById('480p').checked) {
        qualityExclusion.push('480p');
    }
    if (document.getElementById('rips').checked) {
        qualityExclusion.push('rips');
    }
    if (document.getElementById('cam').checked) {
        qualityExclusion.push('cam');
    }
    const languages = [];
    if (document.getElementById('en').checked) {
        languages.push('en')
    }
    if (document.getElementById('fr').checked) {
        languages.push('fr')
    }
    if (document.getElementById('es').checked) {
        languages.push('es')
    }
    if (document.getElementById('de').checked) {
        languages.push('de')
    }
    if (document.getElementById('it').checked) {
        languages.push('it')
    }
    if (document.getElementById('pt').checked) {
        languages.push('pt')
    }
    if (document.getElementById('ru').checked) {
        languages.push('ru')
    }
    if (document.getElementById('in').checked) {
        languages.push('in')
    }
    if (document.getElementById('nl').checked) {
        languages.push('nl')
    }
    if (document.getElementById('hu').checked) {
        languages.push('hu')
    }
    if (document.getElementById('la').checked) {
        languages.push('la')
    }
    if (document.getElementById('multi').checked) {
        languages.push('multi')
    }

    let qualityChecked = document.getElementById('quality').checked;
    let sizedescChecked = document.getElementById('sizedesc').checked;
    let sizeascChecked = document.getElementById('sizeasc').checked;
    let qualitythensizeChecked = document.getElementById('qualitythensize').checked;
    let filter;
    if (qualityChecked) {
        filter = 'quality';
    }
    if (sizedescChecked) {
        filter = 'sizedesc';
    }
    if (sizeascChecked) {
        filter = 'sizeasc';
    }
    if (qualitythensizeChecked) {
        filter = 'qualitythensize';
    }
    if (maxSize === '' || isNaN(maxSize)) {
        maxSize = 0;
    }
    if (maxResults === '' || isNaN(maxResults)) {
        maxResults = 5;
    }
    if (resultsPerQuality === '' || isNaN(resultsPerQuality)) {
        resultsPerQuality = 1;
    }
    let data = {
        addonHost,
        jackettHost,
        'jackettApiKey': jackettApi,
        service,
        'debridKey': debridApi,
        maxSize,
        exclusionKeywords,
        languages,
        'sort': filter,
        resultsPerQuality,
        maxResults,
        'exclusion': qualityExclusion,
        tmdbApi,
        jackett,
        cache,
        torrenting,
        debrid
    };
    if ((jackett && (jackettHost === '' || jackettApi === '')) || (debrid && debridApi === '') || tmdbApi === '' || languages.length === 0) {
        alert('Please fill all required fields');
        return false;
    }
    let stremio_link = `${window.location.host}/${btoa(JSON.stringify(data))}/manifest.json`;

    if (method === 'link') {
        window.open(`stremio://${stremio_link}`, "_blank");
    } else if (method === 'copy') {
        const link = window.location.protocol + '//' + stremio_link;

        if (!navigator.clipboard) {
            alert('Your browser does not support clipboard');
            console.log(link);
            return;
        }

        navigator.clipboard.writeText(link).then(() => {
            alert('Link copied to clipboard');
        }, () => {
            alert('Error copying link to clipboard');
        });
    }
}