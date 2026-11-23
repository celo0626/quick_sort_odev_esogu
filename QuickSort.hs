import Data.List (foldl')

quickSort :: [Int] -> [Int]
quickSort [] = []
quickSort xs =
    let pivotIndex = length xs `div` 2
        pivot = xs !! pivotIndex
        smaller = filter (< pivot) xs
        equalTo = filter (== pivot) xs
        larger = filter (> pivot) xs
    in quickSort smaller ++ equalTo ++ quickSort larger

main :: IO ()
main = do
    input <- getContents
    let values = map read (words input) :: [Int]
        sortedValues = quickSort values
        checksum = foldl' (+) 0 sortedValues
    putStrLn (show (length sortedValues) ++ " " ++ show checksum)
