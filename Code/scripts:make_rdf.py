from __future__ import annotations

import hashlib
from pathlib import Path
from datetime import date

import pandas as pd
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD, DCTERMS, FOAF

# -----------------------------
# CONFIG
# -----------------------------
REPO_OWNER = "KikaYang"
REPO_NAME = "DepressionResearch"
BRANCH = "main"

# PAGES_BASE = f"https://{REPO_OWNER.lower()}.github.io/{REPO_NAME}/"

REPO_BASE = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/"

# downloadURL：raw 
RAW_BASE = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}/"

# 
OUT_DIR = Path("rdf")
OUT_DATA_TTL = OUT_DIR / "mashup_summary_public.ttl"
OUT_DCAT_TTL = OUT_DIR / "dcat-ap.ttl"
OUT_LICENSE_TTL = OUT_DIR / "license.ttl"

# license
OUTPUT_LICENSE_URI = "https://creativecommons.org/licenses/by/4.0/"

DATASET_TITLE = "DepressionResearch mash-up (aggregated trends)"
DATASET_DESCRIPTION = (
    "Aggregated group-level mash-up across multiple Kaggle datasets. "
    "Observations report prevalence rates by harmonised dimensions "
    "(age group, dietary habits, financial hardship bucket, family history), "
    "with student/professional depression rates and a general proxy rate."
)

PUBLISHER_NAME = "DepressionResearch project team"
CONTACT_EMAIL = "mailto:yangtianchi2017@gmail.com" 

# Kaggle (provenance）
KAGGLE_SOURCES = [
    "https://www.kaggle.com/datasets/ikynahidwin/depression-professional-dataset",
    "https://www.kaggle.com/datasets/adilshamim8/student-depression-dataset",
    "https://www.kaggle.com/datasets/anthonytherrien/depression-dataset",
]

TODAY = date.today().isoformat()

# -----------------------------
# Namespaces
# -----------------------------
BASE = REPO_BASE  # 你也可以换成 REPO_BASE
EX = Namespace(BASE + "id/")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
QB = Namespace("http://purl.org/linked-data/cube#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
PROV = Namespace("http://www.w3.org/ns/prov#")
VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")


def find_project_root() -> Path:
    here = Path(__file__).resolve().parent
    candidates = [here, here.parent, here.parent.parent, Path.cwd()]
    for base in candidates:
        if (base / "data/Table/mashup_summary_public.csv").exists():
            return base
        if (base / "mashup_summary_public.csv").exists():
            return base
    return Path.cwd()


def find_csv_path(root: Path) -> Path:
    p1 = root / "data/Table/mashup_summary_public.csv"
    p2 = root / "mashup_summary_public.csv"
    if p1.exists():
        return p1
    if p2.exists():
        return p2
    raise FileNotFoundError(
        f"Could not find mashup_summary_public.csv. Tried: {p1}, {p2}"
    )


def stable_obs_uri(row: dict) -> URIRef:
    keys = [
        "source_dataset",
        "metric_readable",
        "age_group",
        "diet_group",
        "financial_bucket",
        "family_history_flag",
    ]
    raw = "|".join(str(row.get(k, "")) for k in keys)
    h = hashlib.md5(raw.encode("utf-8")).hexdigest()
    return EX[f"observation/{h}"]


def build_data_graph(csv_path: Path) -> Graph:
    df = pd.read_csv(csv_path)

    g = Graph()
    g.bind("ex", EX)
    g.bind("qb", QB)
    g.bind("dct", DCTERMS)
    g.bind("xsd", XSD)
    g.bind("skos", SKOS)
    g.bind("dcat", DCAT)
    g.bind("prov", PROV)

    dataset_uri = EX["dataset/mashup_summary_public"]
    g.add((dataset_uri, RDF.type, DCAT.Dataset))
    g.add((dataset_uri, DCTERMS.title, Literal(DATASET_TITLE, lang="en")))
    g.add((dataset_uri, DCTERMS.description, Literal(DATASET_DESCRIPTION, lang="en")))
    g.add((dataset_uri, DCTERMS.license, URIRef(OUTPUT_LICENSE_URI)))

    for src in KAGGLE_SOURCES:
        g.add((dataset_uri, PROV.wasDerivedFrom, URIRef(src)))
        g.add((dataset_uri, DCTERMS.source, URIRef(src)))

    rate_prop = EX["prop/rate"]
    n_prop = EX["prop/n"]
    g.add((rate_prop, RDF.type, RDF.Property))
    g.add((rate_prop, RDFS.label, Literal("rate")))
    g.add((n_prop, RDF.type, RDF.Property))
    g.add((n_prop, RDFS.label, Literal("n")))

    for _, r in df.iterrows():
        row = r.to_dict()
        obs = stable_obs_uri(row)

        g.add((obs, RDF.type, QB.Observation))
        g.add((obs, DCTERMS.isPartOf, dataset_uri))

        g.add((obs, EX["dim/source_dataset"], Literal(str(row.get("source_dataset")), datatype=XSD.string)))
        g.add((obs, EX["dim/metric"], Literal(str(row.get("metric_readable", row.get("metric"))), datatype=XSD.string)))
        g.add((obs, EX["dim/age_group"], Literal(str(row.get("age_group")), datatype=XSD.string)))
        g.add((obs, EX["dim/diet_group"], Literal(str(row.get("diet_group")), datatype=XSD.string)))
        g.add((obs, EX["dim/financial_bucket"], Literal(str(row.get("financial_bucket")), datatype=XSD.string)))
        g.add((obs, EX["dim/family_history_flag"], Literal(int(row.get("family_history_flag")), datatype=XSD.integer)))

        g.add((obs, rate_prop, Literal(float(row.get("rate")), datatype=XSD.decimal)))
        g.add((obs, n_prop, Literal(int(row.get("n")), datatype=XSD.integer)))

    return g


def build_dcat_graph(csv_rel_path: str) -> Graph:
    g = Graph()
    g.bind("dcat", DCAT)
    g.bind("dct", DCTERMS)
    g.bind("foaf", FOAF)
    g.bind("ex", EX)
    g.bind("xsd", XSD)
    g.bind("prov", PROV)
    g.bind("vcard", VCARD)

    dataset_uri = EX["dataset/mashup_summary_public"]
    dist_csv = EX["distribution/mashup_summary_public_csv"]
    dist_ttl = EX["distribution/mashup_summary_public_ttl"]

    publisher = EX["agent/publisher"]
    contact = EX["agent/contactPoint"]

    # Dataset
    g.add((dataset_uri, RDF.type, DCAT.Dataset))
    g.add((dataset_uri, DCTERMS.title, Literal(DATASET_TITLE, lang="en")))
    g.add((dataset_uri, DCTERMS.description, Literal(DATASET_DESCRIPTION, lang="en")))
    g.add((dataset_uri, DCTERMS.issued, Literal(TODAY, datatype=XSD.date)))
    g.add((dataset_uri, DCTERMS.modified, Literal(TODAY, datatype=XSD.date)))
    g.add((dataset_uri, DCTERMS.license, URIRef(OUTPUT_LICENSE_URI)))

    # provenance
    for src in KAGGLE_SOURCES:
        g.add((dataset_uri, PROV.wasDerivedFrom, URIRef(src)))
        g.add((dataset_uri, DCTERMS.source, URIRef(src)))

    # publisher
    g.add((publisher, RDF.type, FOAF.Organization))
    g.add((publisher, FOAF.name, Literal(PUBLISHER_NAME)))
    g.add((dataset_uri, DCTERMS.publisher, publisher))

    # contactPoint
    g.add((contact, RDF.type, VCARD.Kind))
    g.add((contact, VCARD.hasEmail, URIRef(CONTACT_EMAIL)))
    g.add((dataset_uri, DCAT.contactPoint, contact))

    # Distributions
    csv_download_url = RAW_BASE + csv_rel_path.replace("\\", "/")
    ttl_download_url = RAW_BASE + "rdf/mashup_summary_public.ttl"

    g.add((dataset_uri, DCAT.distribution, dist_csv))
    g.add((dist_csv, RDF.type, DCAT.Distribution))
    g.add((dist_csv, DCTERMS.title, Literal("CSV distribution", lang="en")))
    g.add((dist_csv, DCTERMS.license, URIRef(OUTPUT_LICENSE_URI)))
    g.add((dist_csv, DCAT.mediaType, Literal("text/csv")))
    g.add((dist_csv, DCAT.downloadURL, URIRef(csv_download_url)))

    g.add((dataset_uri, DCAT.distribution, dist_ttl))
    g.add((dist_ttl, RDF.type, DCAT.Distribution))
    g.add((dist_ttl, DCTERMS.title, Literal("RDF Turtle distribution", lang="en")))
    g.add((dist_ttl, DCTERMS.license, URIRef(OUTPUT_LICENSE_URI)))
    g.add((dist_ttl, DCAT.mediaType, Literal("text/turtle")))
    g.add((dist_ttl, DCAT.downloadURL, URIRef(ttl_download_url)))

    return g


def build_license_graph() -> Graph:
    g = Graph()
    g.bind("dct", DCTERMS)

    dataset_uri = EX["dataset/mashup_summary_public"] 
    g.add((dataset_uri, DCTERMS.license, URIRef(OUTPUT_LICENSE_URI)))

    return g


def main():
    root = find_project_root()
    csv_path = find_csv_path(root)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    data_g = build_data_graph(csv_path)
    data_g.serialize(destination=str((root / OUT_DATA_TTL).resolve()), format="turtle")

    csv_rel = str(csv_path.relative_to(root))
    dcat_g = build_dcat_graph(csv_rel)
    dcat_g.serialize(destination=str((root / OUT_DCAT_TTL).resolve()), format="turtle")

    lic_g = build_license_graph()
    lic_g.serialize(destination=str((root / OUT_LICENSE_TTL).resolve()), format="turtle")

    print("✅ RDF generated:")
    print(" -", (root / OUT_DATA_TTL).resolve())
    print(" -", (root / OUT_DCAT_TTL).resolve())
    print(" -", (root / OUT_LICENSE_TTL).resolve())


if __name__ == "__main__":
    main()
