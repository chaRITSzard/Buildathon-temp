const API_BASE_URL = 'http://127.0.0.1:8000'

export async function askNova(question) {
  const response = await fetch(
    `${API_BASE_URL}/ask`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question,
      }),
    }
  )

  const data = await response.json()

  if (!response.ok) {
    throw new Error(
      data.error || 'NOVA request failed.'
    )
  }

  return data
}

export async function decideNova(payload) {
  const response = await fetch(
    `${API_BASE_URL}/decision`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    }
  )

  const data = await response.json()

  if (!response.ok) {
    throw new Error(
      data.error || 'Decision request failed.'
    )
  }

  return data
}

export async function getActions() {
  const response = await fetch(
    `${API_BASE_URL}/actions`
  )

  const data = await response.json()

  if (!response.ok) {
    throw new Error(
      data.error || 'Failed to load action history.'
    )
  }

  return data
}