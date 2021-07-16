// https://stackoverflow.com/a/19366389
const memoize = (factory, ctx) => {
  const cache = {};
  return (key) => {
    if (!(key in cache)) {
      cache[key] = factory.call(ctx, key);
    }
    return cache[key];
  };
};

const colorToRGBA = (() => {
  const canvas = document.createElement('canvas');
  canvas.width = 1;
  canvas.height = 1;
  const ctx = canvas.getContext('2d');

  return memoize((col) => {
    ctx.clearRect(0, 0, 1, 1);
    // In order to detect invalid values,
    // we can't rely on col being in the same format as what fillStyle is computed as,
    // but we can ask it to implicitly compute a normalized value twice and compare.
    ctx.fillStyle = '#000';
    ctx.fillStyle = col;
    const computed = ctx.fillStyle;
    ctx.fillStyle = '#fff';
    ctx.fillStyle = col;
    if (computed !== ctx.fillStyle) {
      return; // invalid color
    }
    ctx.fillRect(0, 0, 1, 1);
    return [...ctx.getImageData(0, 0, 1, 1).data]; // eslint-disable-line
  });
})();

const colorOrFallbackColorToRGBA = (color, fallbackColor) => {
  const fallbackRGBA = colorToRGBA(fallbackColor);
  if (!fallbackRGBA) {
    throw new Error(`Invalid fallbackColor ${
      fallbackColor != null ? JSON.stringify(fallbackColor) : fallbackColor
    }`);
  }
  return colorToRGBA(color) || fallbackRGBA;
};

export default (color) => {
  const [r, g, b] = colorOrFallbackColorToRGBA(color, '#fff');
  return [r, g, b];
};
