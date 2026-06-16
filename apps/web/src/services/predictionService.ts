import type {
  PredictionRequest,
  PredictionResponse,
} from '../types/prediction'

export class PredictionServiceError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'PredictionServiceError'
  }
}

export const PREDICTION_API_URL =
  'http://127.0.0.1:8000/api/v1/predict'

async function parseErrorResponse(response: Response): Promise<string> {
  try {
    const payload: unknown = await response.json()

    if (typeof payload === 'object' && payload !== null) {
      const maybeDetail = (payload as { detail?: unknown }).detail

      if (typeof maybeDetail === 'string' && maybeDetail.trim().length > 0) {
        return maybeDetail
      }
    }
  } catch {
    // Fall back to the generic HTTP status text below.
  }

  return response.statusText || `Request failed with status ${response.status}`
}

function validatePredictionResponse(
  payload: unknown,
): PredictionResponse {
  if (
    typeof payload !== 'object' ||
    payload === null ||
    typeof (payload as { prediction?: unknown }).prediction !== 'string' ||
    typeof (payload as { confidence?: unknown }).confidence !== 'number'
  ) {
    throw new PredictionServiceError('Invalid response received from the prediction API.')
  }

  return {
    prediction: (payload as { prediction: string }).prediction,
    confidence: (payload as { confidence: number }).confidence,
  }
}

export async function predictNews(
  text: string,
): Promise<PredictionResponse> {
  const trimmedText = text.trim()

  if (!trimmedText) {
    throw new PredictionServiceError('Text is required for prediction.')
  }

  try {
    const response = await fetch(PREDICTION_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: trimmedText,
      } satisfies PredictionRequest),
    })

    if (!response.ok) {
      const message = await parseErrorResponse(response)
      throw new PredictionServiceError(message)
    }

    const payload: unknown = await response.json()
    return validatePredictionResponse(payload)
  } catch (error: unknown) {
    if (error instanceof PredictionServiceError) {
      throw error
    }

    const message =
      error instanceof Error && error.message.trim().length > 0
        ? error.message
        : 'Unable to reach the prediction service.'

    throw new PredictionServiceError(message)
  }
}

export type { PredictionRequest, PredictionResponse }
export default predictNews
