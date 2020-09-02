const parseParams = (model, version) => {
  const m = model ? `:${model}` : '';
  const v = version ? `:V${version}` : '';

  return [m, v];
};

export default parseParams;
