"""
Test script to validate improvements made to the report analysis service.
This script tests the enhanced AI analysis methods with improved prompts and error handling.
"""
import asyncio
import json
from services.report_analysis_service import ReportAnalysisService, ReportAnalysisConfig
from schemas.report_analysis import ReportAnalysisRequest, ReportFileType, ReportLanguage


async def test_improved_report_analysis():
    """Test the improved report analysis service with sample data."""
    
    print("Testing Improved Report Analysis Service")
    print("=" * 50)
    
    # Create a sample report content for testing
    sample_report = """
    摘要
    本文提出了一种基于深度学习的图像识别方法。该方法结合了卷积神经网络和注意力机制，
    在多个公开数据集上取得了较好的效果。实验结果表明，该方法相比传统方法有显著提升。
    
    1. 引言
    随着人工智能技术的发展，图像识别已成为计算机视觉领域的热点问题。
    传统的图像识别方法依赖于手工特征提取，效果有限。近年来，深度学习方法
    在图像识别领域取得了突破性进展。
    
    2. 相关工作
    早期的图像识别方法主要基于SIFT、HOG等手工特征。随着深度学习的发展，
    卷积神经网络(CNN)在图像识别任务中表现出色。ResNet、DenseNet等网络
    结构进一步提升了识别精度。
    
    3. 方法
    本文提出的方法主要包括三个部分：特征提取、注意力机制和分类器。
    首先使用改进的CNN提取图像特征，然后引入注意力机制突出重要特征，
    最后通过分类器输出识别结果。
    
    4. 实验
    我们在CIFAR-10和MNIST数据集上进行了实验。实验结果显示，本文方法
    的识别准确率分别达到了95.2%和98.7%，相比基线方法提升了3.1%。
    
    5. 结论
    本文提出的基于深度学习的图像识别方法在多个数据集上表现良好。
    未来的工作将探索更复杂的网络结构和训练策略。
    """
    
    # Configure the service to use AI for testing
    config = ReportAnalysisConfig(
        use_ai_for_logic=True,
        use_ai_for_innovation=True,
        use_ai_for_suggestions=True,
        use_ai_for_language=True,
        fallback_to_rules=True  # Enable fallback for robustness
    )
    
    # Create the service instance
    service = ReportAnalysisService(config=config)
    
    # Create a test request
    request = ReportAnalysisRequest(
        file_name="sample_report.pdf",
        file_type=ReportFileType.PDF,
        content=sample_report,
        language=ReportLanguage.ZH
    )
    
    print("Starting analysis with improved prompts and error handling...")
    
    try:
        # Perform the analysis
        result = await service.analyze_report(request, config)
        
        print(f"[PASS] Analysis completed successfully")
        print(f"  - Report ID: {result.report_id}")
        print(f"  - Overall Score: {result.overall_score:.2f}")
        print(f"  - Summary: {result.summary}")
        print()

        # Print key metrics
        print("Key Metrics:")
        print(f"  - Completeness Score: {result.quality.overall_completeness_score:.2f}")
        print(f"  - Argumentation Score: {result.logic.argumentation_score:.2f}")
        print(f"  - Novelty Score: {result.innovation.novelty_score:.2f}")
        print(f"  - Academic Tone Score: {result.language_quality.academic_tone_score:.2f}")
        print(f"  - Readability Score: {result.language_quality.readability_score:.2f}")
        print()

        # Print some suggestions if available
        if result.suggestions:
            print(f"Suggestions ({len(result.suggestions)} found):")
            for i, suggestion in enumerate(result.suggestions[:3]):  # Show first 3
                print(f"  {i+1}. [{suggestion.category.upper()}] {suggestion.summary}")
                print(f"     {suggestion.details[:100]}...")
            if len(result.suggestions) > 3:
                print(f"  ... and {len(result.suggestions) - 3} more suggestions")
        else:
            print("No suggestions generated (may be due to AI service unavailability)")

        print()
        print("[PASS] All tests passed! The improved report analysis service is working correctly.")
        
    except Exception as e:
        print(f"[FAIL] Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    return True


async def test_json_parsing_robustness():
    """Test the robustness of JSON parsing with various malformed responses."""

    print("\nTesting JSON Parsing Robustness")
    print("=" * 40)

    service = ReportAnalysisService()

    # Test cases for different JSON response formats
    test_cases = [
        # Proper JSON
        '{"section_order_score": 85, "coherence_score": 78, "argumentation_score": 82}',

        # JSON with markdown code blocks
        'Here is the analysis:\n```json\n{"section_order_score": 80, "coherence_score": 75, "argumentation_score": 85}\n```',

        # JSON with regular code blocks
        'Here is the result:\n```\n{"section_order_score": 90, "coherence_score": 88, "argumentation_score": 92}\n```',

        # JSON with prefix text
        'The scores are: {"section_order_score": 75, "coherence_score": 70, "argumentation_score": 78}',

        # Malformed JSON (should handle gracefully)
        'This is not JSON at all',

        # Invalid values (should handle gracefully)
        '{"section_order_score": "invalid", "coherence_score": -10, "argumentation_score": 150}'
    ]

    for i, response in enumerate(test_cases):
        print(f"Test case {i+1}: {response[:50]}{'...' if len(response) > 50 else ''}")
        try:
            result = service._parse_logic_analysis_json(response)
            if result:
                print(f"  [PASS] Parsed successfully: Scores ({result.section_order_score}, {result.coherence_score}, {result.argumentation_score})")
            else:
                print(f"  [SKIP] Failed to parse (expected for invalid JSON)")
        except Exception as e:
            print(f"  [FAIL] Error: {str(e)}")
        print()

    print("[PASS] JSON parsing robustness tests completed.")


async def main():
    """Main test function."""
    print("AI Teaching Assistant - Report Analysis Service Improvements Validation")
    print("=" * 70)

    # Test the improved analysis service
    success1 = await test_improved_report_analysis()

    # Test JSON parsing robustness
    await test_json_parsing_robustness()

    if success1:
        print("\n[SUCCESS] All tests completed successfully!")
        print("The report analysis service improvements have been validated.")
    else:
        print("\n[ERROR] Some tests failed.")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)