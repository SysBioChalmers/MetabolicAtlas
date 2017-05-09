export default function (c) {
  if (c.metabolite) {
    return c.metabolite.hmdb_link || c.metabolite.pubchem_link;
  } else if (c.enzyme) {
    return c.enzyme.uniprot_link || c.enzyme.ensembl_link;
  }

  return null;
}
