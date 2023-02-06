/**
 * Given a js file object representing a jpg or png image, such as one taken
 * from a html file input element, return a promise which resolves to the file
 * data as a data url.
 * More info:
 *   https://developer.mozilla.org/en-US/docs/Web/API/File
 *   https://developer.mozilla.org/en-US/docs/Web/API/FileReader
 *   https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/Data_URIs
 *
 * Example Usage:
 *   const file = document.querySelector('input[type="file"]').files[0];
 *   console.log(fileToDataUrl(file));
 * @param {File} file The file to be read.
 * @return {Promise<string>} Promise which resolves to the file as a data url.
 */

// Have copied this helper function provided in assignment 2 for this assignment 3
export function fileToDataUrl (file) {
  const validFileTypes = ['image/png', 'image/jpeg']
  const valid = validFileTypes.find(type => type === file.type);
  // If the file is not png or jpg, return error and it will be handled in main.js file
  if (!valid) {
    return ('Error');
  }

  const reader = new FileReader();
  reader.readAsDataURL(file);

  const dataUrlPromise = new Promise((resolve, reject) => {
    reader.onerror = reject;
    reader.onload = () => resolve(reader.result);
  });

  return dataUrlPromise;
}
