// Cenas atkarībā no izmēra (Globalais filtrs izmantos šo)
const wheelSizePrices = {
    "R13-R15": 40,
    "R16-R17": 45,
    "R18-R19": 50,
    "R20+ / RunFlat": 60
};

const serviceData = {
    "Riepu serviss": [
        { name: "Montāža + Balansēšana (4 gab.)", price: 0, isDynamic: true }, 
        { name: "Riepu glabāšana (sezona)", price: 30 },
        { name: "Disku mazgāšana ar ķīmiju", price: 15 },
        { name: "Ventiļu maiņa (4 gab.)", price: 10 }
    ],
    "Eļļas un filtri": [
        { name: "Dzinēja eļļas un filtra maiņa (25€ - 35€)", price: 25 },
        { name: "Gaisa filtra maiņa (10€ - 15€)", price: 10 },
        { name: "Salona filtra maiņa (15€ - 25€)", price: 15 },
        { name: "Degvielas filtra maiņa (15€ - 30€)", price: 15 },
        { name: "Automātiskās kārbas eļļas maiņa (80€ - 150€)", price: 80 }
    ],
    "Bremžu sistēma": [
        { name: "PRIEKŠĒJĀ ASS", isHeader: true },
        { name: "Bremžu kluču maiņa (30€ - 50€)", price: 30 },
        { name: "Bremžu disku un kluču maiņa (50€ - 80€)", price: 50 },
        { name: "Suportu profilakse (20€ - 40€)", price: 20 },
        
        { name: "AIZMUGURĒJĀ ASS", isHeader: true },
        { name: "Bremžu kluču maiņa (30€ - 50€)", price: 30 },
        { name: "Bremžu disku un kluču maiņa (50€ - 80€)", price: 50 },
        { name: "Suportu profilakse (20€ - 40€)", price: 20 },
        { name: "Rokasbremzes loku maiņa (40€ - 70€)", price: 40 },
        { name: "Rokasbremzes trošu maiņa (30€ - 60€)", price: 30 },
        { name: "Rokasbremzes regulēšana (25€ - 40€)", price: 25 },

        { name: "PAPILDDARBI UN SISTĒMA", isHeader: true },
        { name: "Bremžu šķidruma maiņa ar atgaisošanu (30€ - 50€)", price: 30 },
        { name: "Suporta pilna restaurācija 1 gab. (45€ - 80€)", price: 45 },
        { name: "Bremžu cauruļu maiņa (no 40€)", price: 40 },
        { name: "Bremžu sistēmas atgaisošana (15€ - 30€)", price: 15 }
    ],
    "Ritošā daļa": [
        { name: "VISPĀRĒJIE DARBI", isHeader: true },
        { name: "Ritošās daļas diagnostika (no 20€)", price: 20 },

        { name: "PRIEKŠĒJĀ ASS", isHeader: true },
        { name: "Amortizatora maiņa (45€ - 80€)", price: 45, hasSides: true },
        { name: "Amortizatora atsperes maiņa (40€ - 70€)", price: 40, hasSides: true },
        { name: "Riteņa gultņa maiņa (50€ - 90€)", price: 50, hasSides: true },
        { name: "Sviras vai bukses maiņa (35€ - 70€)", price: 35, hasSides: true },
        { name: "Stabilizatora atsaites maiņa (15€ - 30€)", price: 15, hasSides: true },
        { name: "Stūres pirksta vai stieņa maiņa (25€ - 45€)", price: 25, hasSides: true },
        { name: "Pusass (granātas) maiņa (40€ - 80€)", price: 40, hasSides: true },

        { name: "AIZMUGURĒJĀ ASS", isHeader: true },
        { name: "Amortizatora maiņa (45€ - 80€)", price: 45, hasSides: true },
        { name: "Amortizatora atsperes maiņa (40€ - 70€)", price: 40, hasSides: true },
        { name: "Riteņa gultņa maiņa (50€ - 90€)", price: 50, hasSides: true },
        { name: "Sviras vai bukses maiņa (35€ - 70€)", price: 35, hasSides: true },
        { name: "Stabilizatora atsaites maiņa (15€ - 30€)", price: 15, hasSides: true }
    ],
    "Dzinējs un transmisija": [
        { name: "VISPĀRĒJIE DARBI", isHeader: true, fuel: 'all' },
        { name: "Zobsiksnas komplekta maiņa (150€ - 300€)", price: 150, fuel: 'all' },
        { name: "Dzinēja ķēdes komplekta maiņa (no 250€)", price: 250, fuel: 'all' },
        { name: "Ģeneratora / celiņsiksnas maiņa (30€ - 60€)", price: 30, fuel: 'all' },
        { name: "Sajūga un/vai spararata komplekta maiņa (no 200€)", price: 200, fuel: 'all' },
        { name: "Manuālās ātrumkārbas noņemšana/uzlikšana (no 150€)", price: 150, fuel: 'all' },
        { name: "Vārstu vāka blīves maiņa (40€ - 80€)", price: 40, fuel: 'all' },
        { name: "Kartera blīves vai hermētiķa pārblīvēšana (no 50€)", price: 50, fuel: 'all' },
        { name: "Turbīnas noņemšana un uzstādīšana (no 100€)", price: 100, fuel: 'all' },
        { name: "Termostata maiņa (30€ - 80€)", price: 30, fuel: 'all' },
        { name: "Ūdenssūkņa maiņa (no 50€)", price: 50, fuel: 'all' },
        { name: "Dzinēja spilvena maiņa (30€ - 80€)", price: 30, fuel: 'all' },

        { name: "BENZĪNA DZINĒJU DARBI", isHeader: true, fuel: 'petrol' },
        { name: "Aizdedzes sveču maiņa komplektam (30€ - 80€)", price: 30, fuel: 'petrol' },
        { name: "Aizdedzes spoļu maiņa 1 gab. (15€ - 30€)", price: 15, fuel: 'petrol' },
        { name: "Droseļvārsta tīrīšana un adaptācija (30€ - 60€)", price: 30, fuel: 'petrol' },
        { name: "Lambda zondes (skābekļa sensora) maiņa (20€ - 50€)", price: 20, fuel: 'petrol' },

        { name: "DĪZEĻDZINĒJU DARBI", isHeader: true, fuel: 'diesel' },
        { name: "Kvēlsveču maiņa 1 gab. (25€ - 50€)", price: 25, fuel: 'diesel' },
        { name: "Kvēlsveču releja maiņa (no 30€)", price: 30, fuel: 'diesel' },
        { name: "Degvielas sprauslu blīvgredzenu (šaibu) maiņa (no 60€)", price: 60, fuel: 'diesel' },
        { name: "Degvielas sprauslu noņemšana/uzstādīšana 1 gab. (no 40€)", price: 40, fuel: 'diesel' },
        { name: "EGR vārsta tīrīšana vai maiņa (50€ - 100€)", price: 50, fuel: 'diesel' }
    ],
    "Elektrosistēma": [
        { name: "DIAGNOSTIKA UN ELEKTRIKA", isHeader: true },
        { name: "Datoru diagnostika, kļūdu lasīšana un dzēšana (no 25€)", price: 25 },
        { name: "Dziļā diagnostika un parametru pārbaude (dzīvajos datos) (no 40€)", price: 40 },
        { name: "Akumulatora pārbaude un maiņa (15€ - 25€)", price: 15 },
        { name: "Lukturu spuldžu maiņa (5€ - 30€)", price: 5 },
        { name: "Lukturu regulēšana (15€ - 20€)", price: 15 },
        { name: "Parkošanās sensoru pārbaude un maiņa (no 30€)", price: 30 },
        { name: "Vadu un savienojumu remonts (no 40€/h)", price: 40 },

        { name: "STARTERI UN ĢENERATORI", isHeader: true },
        { name: "Ģeneratora noņemšana / uzstādīšana (40€ - 80€)", price: 40 },
        { name: "Startera noņemšana / uzstādīšana (40€ - 80€)", price: 40 },
        { name: "Ģeneratora vai startera remonts (no 60€)", price: 60 },

        { name: "CHIPTUNING UN PROGRAMMĒŠANA", isHeader: true },
        { name: "Jaudas palielināšana (Chiptuning / Stage 1) (no 150€)", price: 150 },
        { name: "EGR vārsta programmiska atslēgšana (no 80€)", price: 80 },
        { name: "DPF / FAP filtra programmiska atslēgšana (no 100€)", price: 100 },
        { name: "AdBlue (SCR) sistēmas programmiska atslēgšana (no 150€)", price: 150 },
        { name: "IMMO (Imobilaizera) atslēgšana (no 80€)", price: 80 },
        { name: "Specifisku kļūdu (DTC) programmiska dzēšana (no 50€)", price: 50 }
    ],
    "Izplūdes sistēma un metināšana": [
        { name: "IZPLŪDES SISTĒMA", isHeader: true },
        { name: "Izpūtēja gofras maiņa (no 30€)", price: 30 },
        { name: "Izpūtēja bunduļa maiņa (no 40€)", price: 40 },
        { name: "Katalizatora vai DPF fiziska izgriešana (no 50€)", price: 50 },
        { name: "Izplūdes sistēmas blīvju maiņa (no 20€)", price: 20 },

        { name: "METINĀŠANAS DARBI", isHeader: true },
        { name: "Izpūtēja caurumu metināšana (no 20€)", price: 20 },
        { name: "Sliekšņu vai grīdas metināšana (no 50€)", price: 50 },
        { name: "Sarūsējušu skrūvju / uzgriežņu karsēšana un urbšana (no 20€)", price: 20 }
    ],
    "Auto pārbaudes un TA": [
        { name: "PĀRBAUDES", isHeader: true },
        { name: "Auto sagatavošana Tehniskajai apskatei (pārbaude) (no 30€)", price: 30 },
        { name: "Pirmspirkuma pārbaude (Ritošā daļa + Dators + Virsbūve) (no 40€)", price: 40 },
        
        { name: "TA IZIEŠANA KLIENTA VIETĀ", isHeader: true },
        // --- JAUNUMS: Slaidera iestatījums (0-5 stundas, 30€/h) ---
        { name: "Tehniskās apskates iziešana", isSlider: true, price: 30, max: 5 }
    ]
};