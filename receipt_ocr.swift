// Local macOS OCR helper. Receipt bytes enter through stdin and stay in memory.
import Foundation
import Vision
import ImageIO

do {
    let data = FileHandle.standardInput.readDataToEndOfFile()
    guard let source = CGImageSourceCreateWithData(data as CFData, nil),
          let image = CGImageSourceCreateImageAtIndex(source, 0, nil) else {
        throw NSError(domain: "ReceiptScanner", code: 1,
                      userInfo: [NSLocalizedDescriptionKey: "Cannot read receipt image."])
    }
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.recognitionLanguages = ["en-US"]
    request.usesLanguageCorrection = true
    try VNImageRequestHandler(cgImage: image, options: [:]).perform([request])

    // Join words on the same row so separately detected totals retain their label.
    let observations = (request.results ?? []).sorted {
        $0.boundingBox.midY > $1.boundingBox.midY
    }
    var rows: [[VNRecognizedTextObservation]] = []
    for observation in observations {
        if let last = rows.last, let anchor = last.first,
           abs(anchor.boundingBox.midY - observation.boundingBox.midY)
               < min(anchor.boundingBox.height, observation.boundingBox.height) * 0.5 {
            rows[rows.count - 1].append(observation)
        } else {
            rows.append([observation])
        }
    }
    let lines = rows.map { row in
        row.sorted { $0.boundingBox.minX < $1.boundingBox.minX }
            .compactMap { $0.topCandidates(1).first?.string }.joined(separator: " ")
    }
    let result = try JSONSerialization.data(withJSONObject: ["text": lines.joined(separator: "\n")])
    FileHandle.standardOutput.write(result)
} catch {
    FileHandle.standardError.write(Data("Receipt text recognition failed: \(error.localizedDescription)\n".utf8))
    exit(1)
}
