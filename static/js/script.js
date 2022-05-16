function handleError(xhr) {
  $(".action__btn").effect( "shake", { times: 4, distance: 2, }, 500 )
  $(".action > .error").text(xhr?.responseJSON?.description ?? xhr.statusText)
}

const validate = {
  postcode: (value) => {
    // loosely validating postcode beforehand, false positives will be detected on request
    const valid = /^[A-Z]{1,2}\d[A-Z\d]? ?\d[A-Z]{2}$/.test(value)
    return [valid, valid ? "" : "Invalid postcode"]
  }
}

function processForm(e) {
  let formValid = true
  const fields = {}
  // looping through elements in form
  for (const el of $("#form").serializeArray()) {
    // validating form element if theres is a validation function for it
    const [valid, msg] = validate[el.name]?.(el.value) ?? [true, ""]
    if (!valid) {
      // shaking the button if invalid (only once)
      if(formValid) {
        $(".action__btn").effect( "shake", { times: 4, distance: 2 }, 500 )
        formValid = false
      }
      // displaying error message
      $(`#${el.name}`).siblings(".error").text(msg)
      continue // skipping execution of following lines
    }
    // field is valid
    fields[el.name] = el.value
    // resetting error message
    $(`#${el.name}`).siblings(".error").text(msg)
  }
  return [ formValid, fields ]
}

// adding suffix to numbers,
// e.g: 178,000 -> 178k, 1,567,600 -> 1.57M
const ranges = [
  { divider: 1e6 , suffix: 'M' },
  { divider: 1e3 , suffix: 'k' }
]
function formatNumber(n, precision) {
  for (var i = 0; i < ranges.length; i++) {
    if (n >= ranges[i].divider) {
      return (n / ranges[i].divider).toPrecision(precision).toString() + ranges[i].suffix
    }
  }
  return n.toString() // suffix not found so returning
}

let map
function submitForm(e) {
  e.preventDefault()
  $(".action > .error").text("") // resetting form error 
  
  // processing/validating form
  const [ valid, fields ] = processForm(e)
  if (!valid) return false // break execution if invalid

  // finding coordinates from postcode
  $.ajax({
    async: false,
    method: "GET",
    url: `https://api.postcodes.io/postcodes/${fields.postcode}`,
    success: resp => { coords = { lat: resp.result.latitude, lng: resp.result.longitude } },
    error: handleError
  })

  // setting up model parameters with 75% prediction interval
  const params = { ...fields, ...coords, alpha:.25 }
  delete params.postcode

  // sending backend API request
  $.ajax({
    method:"POST",
    url: "/api/price/",
    data: JSON.stringify(params),
    contentType: "application/json charset=utf-8",
    dataType: "json",
    success: res => {
      // displaying output to user
      $("#output__postcode").text(fields.postcode.toUpperCase())
      $("#output__year").text(fields.year)
      $("#output__point").text("£"+parseInt( Math.round(res.point / 100) * 100 ).toLocaleString()) // to nearest hundred
      $("#output__low").text("£"+formatNumber(res.low, 3))
      $("#output__high").text("£"+formatNumber(res.high, 3))
      // map according to given postcode
      map = new google.maps.Map($("#map")[0], {
        center: coords,
        disableDefaultUI: true,
        zoom: 17
      })
      window.location.replace("#output") // "redirecting" to modal window
    },
    error: handleError
  })
  return false
}

$(function () {
  $("#form").submit(submitForm)
})
