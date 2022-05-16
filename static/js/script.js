function handleError(xhr) {
  $(".action__btn").effect( "shake", { times: 4, distance: 2, }, 500 )
  $(".action > .error").text(xhr?.responseJSON?.description ?? xhr.statusText)
}

const validate = {
  postcode: (value) => {
    let valid = false
    $.ajax({
      async:false,
      method:"GET",
      url:`https://api.postcodes.io/postcodes/${value}/validate`,

      success: resp => { valid = resp.result },
      error: () => { valid = /^[A-Z]{1,2}\d[A-Z\d]? ?\d[A-Z]{2}$/.test(value) },
    })

    return [valid, valid ? "" : "Enter a valid postcode"]
  }
}


function processForm(e) {
  let formValid = true
  const fields = {}
  for (const el of $("#form").serializeArray()) {
    const [valid, msg] = validate[el.name]?.(el.value) ?? [true, ""]
    if (!valid) {
      if(formValid) {
        $(".action__btn").effect( "shake", { times: 4, distance: 2 }, 500 )
        formValid = false
      }
      $(`#${el.name}`).siblings(".error").text(msg)
      continue
    }
    fields[el.name] = el.value
    $(`#${el.name}`).siblings(".error").text(msg)
  }
  return [ formValid, fields ]
}

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
  return n.toString()
}

let map
function submitForm(e) {
  e.preventDefault()
  $(".action > .error").text("")
  
  const [ valid, fields ] = processForm(e)
  if (!valid) return false

  $.ajax({
    async: false,
    method: "GET",
    url: `https://api.postcodes.io/postcodes/${fields.postcode}`,
    success: resp => { coords = { lat: resp.result.latitude, lng: resp.result.longitude } },
    error: handleError
  })

  const params = { ...fields, ...coords, alpha:.25 }
  delete params.postcode
  
  $.ajax({
    method:"POST",
    url: "/api/price/",
    data: JSON.stringify(params),
    contentType: "application/json charset=utf-8",
    dataType: "json",
    success: res => {
      $("#output__postcode").text(fields.postcode.toUpperCase())
      $("#output__year").text(fields.year)

      $("#output__point").text("£"+parseInt( Math.round(res.point / 100) * 100 ).toLocaleString())
      $("#output__low").text("£"+formatNumber(res.low, 3))
      $("#output__high").text("£"+formatNumber(res.high, 3))

      map = new google.maps.Map($("#map")[0], {
        center: coords,
        disableDefaultUI: true,
        zoom: 17
      })

      window.location.replace("#output")
    },
    error: handleError
  })

  return false
}

$(function () {
  $("#form").submit(submitForm)
})
