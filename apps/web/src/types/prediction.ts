export interface PredictionRequest {
  text: string
}

export interface PredictionResponse {
  prediction: string
  confidence: number
}
